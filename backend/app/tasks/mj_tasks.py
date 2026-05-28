from flask import current_app
from app.models.mj_task import MJTask, MJTaskStatus
from app.services.mj_service import MJService
from app import db,celery
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@celery.task(bind=True)
def check_mj_task_statuses(self):
    """定时检查 MJ 任务状态"""
    try:
        # 获取所有进行中的任务
        tasks = MJTask.query.filter(
            MJTask.status.in_([
                MJTaskStatus.WAITING,
                MJTaskStatus.IN_PROCESSING
            ])
        ).all()

        if not tasks:
            logger.info("No MJ tasks to check")
            return "No tasks to check"

        logger.info(f"Found {len(tasks)} MJ tasks to check")

        # 初始化 MJ 服务
        mj_service = MJService(
            base_url=current_app.config['MJ_API_URL'],
            api_key=current_app.config['MJ_API_KEY']
        )

        processed_count = 0
        success_count = 0
        failed_count = 0

        for task in tasks:
            try:
                logger.info(f"Checking MJ task {task.id} (status: {task.status})")
                
                # 查询任务状态
                response = mj_service.query_progress(task.user_imagine_id)
                
                if not response.success:
                    logger.error(f"Invalid response for task {task.id}: {response}")
                    # save to db 
                    task.status = MJTaskStatus.FAIL
                    task.error_show = response.error
                    db.session.commit()
                    continue

                logger.warning(f"Task {task.id} response: {response}")
                result = response.data.get('result', {})
                api_status = result.get('taskStatus',{}).get('code')
                logger.info(f"Task {task.id} API status: {api_status}")

                # 更新基本信息
                task.oss_image_url = result.get('ossImageUrl', task.oss_image_url)
                task.image_id = result.get('imageId', task.image_id)
                task.actions_json = result.get('actionsJson', task.actions_json)
                # 状态映射和处理
                if api_status == "SUCCESS":
                    task.status = MJTaskStatus.SUCCESS
                    success_count += 1
                    logger.info(f"Task {task.id} completed successfully")
                
                elif api_status == "FAIL":
                    task.status = MJTaskStatus.FAIL
                    task.error_show = result.get('errorShow', task.error_show)
                    failed_count += 1
                    logger.warning(f"Task {task.id} failed: {task.error_message}")
                
                elif api_status == "CANCEL":
                    task.status = MJTaskStatus.CANCEL
                    logger.info(f"Task {task.id} was cancelled")
                
                elif api_status == "IN_PROCESSING":
                    if task.status == MJTaskStatus.WAITING:
                        task.status = MJTaskStatus.IN_PROCESSING
                        logger.info(f"Task {task.id} moved to IN_PROCESSING")
                
                elif api_status == "WAITING":
                    # 如果已经是 IN_PROCESSING，不要回退状态
                    if task.status != MJTaskStatus.IN_PROCESSING:
                        task.status = MJTaskStatus.WAITING
                        logger.info(f"Task {task.id} is waiting")

                # 更新API相关时间
                task.api_call_at = datetime.utcnow()
                if task.is_completed:
                    task.api_end_at = datetime.utcnow()

                processed_count += 1
                db.session.commit()

            except Exception as e:
                logger.error(f"Error processing task {task.id}: {e}", exc_info=True)
                db.session.rollback()
                continue

        summary = f"Processed {processed_count} tasks: {success_count} succeeded, {failed_count} failed"
        logger.info(summary)
        return summary

    except Exception as e:
        logger.error(f"Task check failed: {e}", exc_info=True)
        return f"Error: {str(e)}"
