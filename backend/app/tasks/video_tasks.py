import logging
from flask import current_app
from datetime import datetime, timezone, timedelta

from ..models.video_task import VideoTask, TaskStatus
from ..utils.video_generator import AlibabaVideoGenerator, AlibabaVideoGeneratorError
from ..utils.obs_uploader import (
    upload_video_from_url_to_obs,
    ObsUploadError,
)
from app import db,celery

# 配置URL有效期（秒）
URL_VALIDITY_PERIOD = 7 * 24 * 3600  # 6天，可以根据需要调整

logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=120)
def check_video_task_statuses(self):
    """
    Celery task to periodically check the status of ongoing video generation tasks.

    Queries Alibaba Cloud for tasks in PROCESSING or QUEUED state and updates
    the local database accordingly.
    It includes a check within the loop to avoid processing tasks already marked
    as completed/failed in the database.
    """
    logger.info("Starting check_video_task_statuses task...")

    tasks_to_check_ids = []
    try:
        # Fetch only the IDs of tasks to potentially check
        tasks_to_check_ids = [
            t.id for t in
            VideoTask.query.with_entities(VideoTask.id).filter(
                VideoTask.status.in_([TaskStatus.PROCESSING, TaskStatus.QUEUED]),
                VideoTask.aliyun_task_id.isnot(None)
            ).limit(50).all()
        ]

        if not tasks_to_check_ids:
            logger.info("No video tasks found in PROCESSING or QUEUED state with aliyun_task_id.")
            return "No tasks to check."

        logger.info(f"Found {len(tasks_to_check_ids)} potential tasks to check.")

        # Initialize the generator once
        try:
            api_key = current_app.config.get('DASHSCOPE_API_KEY')
            generator = AlibabaVideoGenerator(api_key=api_key)
        except ValueError as e:
            logger.error(f"Failed to initialize AlibabaVideoGenerator: {e}. Ensure DASHSCOPE_API_KEY is set.")
            return "Generator initialization failed."

    except Exception as e:
        logger.error(f"Error querying task IDs from database: {e}", exc_info=True)
        return "Database query failed."

    processed_count = 0
    failed_count = 0
    succeeded_count = 0
    skipped_count = 0

    for task_id in tasks_to_check_ids:
        try:
            # Get the task object within the loop to ensure fresh state check
            task = VideoTask.query.get(task_id)
            if not task:
                logger.warning(f"Task ID {task_id} not found in database, skipping.")
                skipped_count += 1
                continue

            # --- Check DB status before calling API --- #
            if task.status not in [TaskStatus.PROCESSING, TaskStatus.QUEUED]:
                logger.debug(f"Task {task.id} is already in state {task.status}, skipping API check.")
                skipped_count += 1
                continue
            # --- End DB status check --- #

            if not task.aliyun_task_id:
                 logger.warning(f"Task {task.id} is in processing state but missing aliyun_task_id, skipping.")
                 skipped_count += 1
                 continue

            logger.debug(f"Checking status for internal task ID: {task.id}, aliyun_task_id: {task.aliyun_task_id}")

            result = generator.query_task_status(task.aliyun_task_id)
            output = result.get("output", {})
            aliyun_status = output.get("task_status")
            request_id = result.get("request_id")

            logger.debug(f"Task {task.id}: Alibaba API raw response output: {output}")

            # --- Process based on Alibaba status --- #
            if aliyun_status == "SUCCEEDED":
                logger.info(f"Task {task.id} ({task.aliyun_task_id}) SUCCEEDED.")
                video_url_aliyun = output.get("video_url")
                if not video_url_aliyun:
                    logger.error(f"Task {task.id} SUCCEEDED but no video_url found: {output}")
                    task.set_failure(error_code="MissingVideoURL", error_message="Task succeeded but Alibaba response missing video URL.")
                    failed_count += 1
                    continue
                try:
                    logger.info(f"Processing OBS upload for task {task.id}")
                    obs_object_key, obs_preview_url = upload_video_from_url_to_obs(
                        video_url=video_url_aliyun,
                        user_id=str(task.user_id),
                        task_id=str(task.id),
                        obs_config={
                            "OBS_ACCESS_KEY": current_app.config.get('OBS_ACCESS_KEY'),
                            "OBS_SECRET_KEY": current_app.config.get('OBS_SECRET_KEY'),
                            "OBS_ENDPOINT": current_app.config.get('OBS_ENDPOINT'),
                            "OBS_BUCKET": current_app.config.get('OBS_BUCKET'),
                        }
                    )
                    # 计算URL过期时间
                    url_expires_at = datetime.now(timezone.utc) + timedelta(seconds=URL_VALIDITY_PERIOD)
                    # 保存成功状态，包括obs_object_key和过期时间
                    task.set_success(
                        video_url=obs_preview_url,
                        obs_object_key=obs_object_key,
                        url_expires_at=url_expires_at
                    )
                    succeeded_count += 1
                except ObsUploadError as upload_err:
                    logger.error(f"OBS upload failed for task {task.id}: {upload_err}")
                    task.set_failure(error_code="ObsUploadFailed", error_message=f"OBS upload failed: {upload_err}")
                    failed_count += 1
                except Exception as general_upload_err:
                    logger.error(f"Unexpected OBS processing error for task {task.id}: {general_upload_err}", exc_info=True)
                    task.set_failure(error_code="ObsProcessingError", error_message=f"Internal error: {general_upload_err}")
                    failed_count += 1

            elif aliyun_status == "FAILED":
                error_code = output.get("code", "UnknownError")
                error_message = output.get("message", "Task failed without specific message.")
                logger.warning(f"Task {task.id} ({task.aliyun_task_id}) FAILED. Code: {error_code}, Msg: {error_message}")
                task.set_failure(error_code=f"AliCloud.{error_code}", error_message=error_message)
                failed_count += 1

            elif aliyun_status == "API_ERROR":
                error_code = output.get("code", "ApiQueryFailed")
                error_message = output.get("message", "Failed to query Alibaba API status.")
                logger.error(f"API Error checking task {task.id} ({task.aliyun_task_id}). Code: {error_code}, Msg: {error_message}")
                # Let retry handle API query errors, do not change DB status here
                pass

            elif aliyun_status in ["PENDING", "RUNNING"]:
                logger.debug(f"Task {task.id} ({task.aliyun_task_id}) is still {aliyun_status}. Ensuring DB status is PROCESSING.")
                if task.status == TaskStatus.QUEUED:
                    task.set_status(TaskStatus.PROCESSING, commit=True)
                # Otherwise, status is already PROCESSING, no change needed
                pass

            else:
                logger.warning(f"Task {task.id} ({task.aliyun_task_id}) has unexpected status: {aliyun_status}. Response: {output}")
                task.set_failure(error_code="UnexpectedStatus", error_message=f"Alibaba API unexpected status: {aliyun_status}")
                failed_count += 1

            processed_count += 1

        # --- Error handling for the loop iteration --- #
        except AlibabaVideoGeneratorError as api_err:
            logger.error(f"Alibaba API error checking task {task_id}: {api_err}", exc_info=True)
            # Let Celery retry mechanism handle temporary API issues
            pass
        except Exception as e:
            logger.error(f"Unexpected error processing task {task_id}: {e}", exc_info=True)
            # Attempt to mark task as failed in DB to avoid loop on persistent errors
            try:
                # Fetch task again in except block if needed, or check if 'task' is bound
                if 'task' in locals() and task is not None:
                    task.set_failure(error_code="TaskProcessingError", error_message=f"Internal error: {e}")
                    failed_count += 1
                else:
                    # If task object couldn't be fetched initially
                    logger.error(f"Could not mark task {task_id} as failed because object was not loaded.")
            except Exception as db_err:
                logger.error(f"Failed to mark task {task_id} as FAILED in DB after error: {db_err}", exc_info=True)
                db.session.rollback()

    summary = f"Finished checking video tasks. Total considered: {len(tasks_to_check_ids)}, API calls attempted: {processed_count}, Skipped (already final state): {skipped_count}, Succeeded: {succeeded_count}, Failed: {failed_count}."
    logger.info(summary)
    return summary

@celery.task(bind=True, max_retries=3, default_retry_delay=300)
def refresh_video_urls(self):
    """定期刷新视频URL的签名
    
    检查即将过期（24小时内）的视频URL，重新生成签名URL
    """
    try:
        current_time = datetime.now(timezone.utc)
        refresh_threshold = current_time + timedelta(hours=24)
        
        tasks = VideoTask.query.filter(
            VideoTask.status == 'SUCCEEDED',
            VideoTask.url_expires_at <= refresh_threshold,
            VideoTask.obs_object_key.isnot(None)
        ).all()
        
        if not tasks:
            logger.info("No video URLs need refresh")
            return "No video URLs need refresh"
            
        logger.info(f"Found {len(tasks)} video URLs need refresh")
            
        # 初始化OBS客户端 - 修复：传入配置参数
        from ..utils.obs_uploader import initialize_obs_client, generate_signed_url
        from flask import current_app
        
        obs_config = {
            'OBS_ACCESS_KEY': current_app.config['OBS_ACCESS_KEY'],
            'OBS_SECRET_KEY': current_app.config['OBS_SECRET_KEY'],
            'OBS_ENDPOINT': current_app.config['OBS_ENDPOINT'],
            'OBS_BUCKET': current_app.config['OBS_BUCKET'],
        }
        
        obs_client = initialize_obs_client(obs_config)
        bucket_name = current_app.config['OBS_BUCKET']
        
        # 更新每个任务的URL
        success_count = 0
        failed_count = 0
        
        for task in tasks:
            try:
                new_signed_url = generate_signed_url(
                    obs_client=obs_client,
                    bucket_name=bucket_name,
                    object_key=task.obs_object_key
                )
                
                # 更新任务记录
                task.video_url = new_signed_url
                task.url_expires_at = current_time + timedelta(days=7)
                db.session.add(task)
                db.session.commit()
                
                logger.info(f"Refreshed URL for task {task.id}")
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to refresh URL for task {task.id}: {e}")
                failed_count += 1
                db.session.rollback()
                continue
                
        result = f"Refreshed URLs for {success_count} out of {len(tasks)} tasks, {failed_count} failed"
        logger.info(result)
        return result
        
    except Exception as e:
        logger.error(f"Video URL refresh task failed: {e}")
        # 如果是临时性错误（如网络问题），可以重试
        self.retry(exc=e)

# --- Celery Beat Configuration --- #
# You need to configure Celery Beat to run this task periodically.
# This usually happens where you initialize your Celery app.
# Example (in your celery setup file, e.g., celery_app.py or tasks/__init__.py):
#
# from celery.schedules import crontab
#
# celery_app.conf.beat_schedule = {
#     'check-video-tasks-every-30-seconds': {
#         'task': 'backend.app.tasks.video_tasks.check_video_task_statuses', # Adjust path if needed
#         'schedule': 30.0, # Run every 30 seconds
#         #'schedule': crontab(minute='*/1'), # Or run every minute using crontab
#     },
# }
# celery_app.conf.timezone = 'Asia/Shanghai' # Set your timezone 
