import requests
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AlibabaVideoGeneratorError(Exception):
    """Custom exception for Alibaba Video Generator errors."""
    def __init__(self, message: str, code: Optional[str] = None, request_id: Optional[str] = None):
        super().__init__(message)
        self.code = code
        self.request_id = request_id

    def __str__(self):
        return f"{self.code}: {self.message} (Request ID: {self.request_id})" if self.code else f"{self.message} (Request ID: {self.request_id})"


class AlibabaVideoGenerator:
    """
    A client for interacting with the Alibaba Cloud DashScope Text-to-Video API.

    Handles creating video generation tasks and querying their status.
    """
    BASE_URL = "https://dashscope.aliyuncs.com/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes the AlibabaVideoGenerator client.

        Args:
            api_key (Optional[str]): The DashScope API key. If None, it attempts
                                     to read from the DASHSCOPE_API_KEY environment variable.

        Raises:
            ValueError: If the API key is not provided and not found in environment variables.
        """
        self.api_key = api_key or os.environ.get("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set as DASHSCOPE_API_KEY environment variable.")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def create_video_task(
        self,
        prompt: str,
        model: str = "wanx2.1-t2v-turbo",
        size: str = "1280*720",
        **kwargs: Any
    ) -> str:
        """
        Submits a request to generate a video based on a text prompt.

        Args:
            prompt (str): The text prompt describing the video content.
            model (str): The model name to use for generation. Defaults to "wanx2.1-t2v-turbo".
            size (str): The desired video resolution (e.g., "1280*720"). Defaults to "1280*720".
            **kwargs: Additional parameters to pass to the API's 'parameters' field.

        Returns:
            str: The task ID assigned by the API for the video generation task.

        Raises:
            AlibabaVideoGeneratorError: If the API request fails or returns an error status.
            requests.exceptions.RequestException: For network-related errors during the API call.
        """
        url = f"{self.BASE_URL}/services/aigc/video-generation/video-synthesis"
        payload = {
            "model": model,
            "input": {"prompt": prompt},
            "parameters": {"size": size, **kwargs},
        }
        # Enable async mode as specified in the docs
        async_headers = {**self.headers, "X-DashScope-Async": "enable"}

        try:
            logger.info(f"Creating video task with prompt: {prompt[:50]}...")
            response = requests.post(url, headers=async_headers, json=payload, timeout=30) # 30 second timeout for initiating
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            request_id = data.get("request_id")
            output = data.get("output", {})
            task_id = output.get("task_id")
            task_status = output.get("task_status")

            if not task_id or task_status != "PENDING":
                # Handle cases where the task wasn't successfully initiated
                error_code = data.get("code", "UnknownError")
                error_message = data.get("message", "Failed to initiate task properly.")
                logger.error(f"Failed to create video task. API Response: {data}")
                raise AlibabaVideoGeneratorError(error_message, code=error_code, request_id=request_id)

            logger.info(f"Video task created successfully. Task ID: {task_id}")
            return task_id

        except requests.exceptions.HTTPError as http_err:
            error_content = http_err.response.text
            logger.error(f"HTTP error occurred during task creation: {http_err} - {error_content}")
            # Try to parse error details from response if possible
            try:
                error_data = http_err.response.json()
                error_code = error_data.get("code", f"HTTP_{http_err.response.status_code}")
                error_message = error_data.get("message", str(http_err))
                request_id = error_data.get("request_id")
                raise AlibabaVideoGeneratorError(error_message, code=error_code, request_id=request_id) from http_err
            except ValueError: # If response is not JSON
                raise AlibabaVideoGeneratorError(f"HTTP error {http_err.response.status_code}: {error_content}", code=f"HTTP_{http_err.response.status_code}") from http_err
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error occurred during task creation: {req_err}")
            raise AlibabaVideoGeneratorError(f"Network or request error: {req_err}") from req_err
        except Exception as e:
            logger.error(f"An unexpected error occurred during task creation: {e}", exc_info=True)
            raise AlibabaVideoGeneratorError(f"An unexpected error occurred: {e}")


    def query_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Queries the status and result of a video generation task.

        Args:
            task_id (str): The ID of the task to query.

        Returns:
            Dict[str, Any]: A dictionary containing the task details, including status,
                            video URL (if succeeded), or error information (if failed).
                            Example successful output structure from API docs:
                            {
                                "request_id": "...",
                                "output": {
                                    "task_id": "...",
                                    "task_status": "SUCCEEDED", // PENDING, RUNNING, FAILED, SUCCEEDED
                                    "submit_time": "...",
                                    "scheduled_time": "...",
                                    "end_time": "...",
                                    "video_url": "..." // Only if SUCCEEDED
                                    // "code": "...", "message": "..." // Only if FAILED
                                },
                                "usage": { ... } // Optional usage details
                            }


        Raises:
            AlibabaVideoGeneratorError: If the API request fails or returns an unexpected format.
            requests.exceptions.RequestException: For network-related errors during the API call.
        """
        url = f"{self.BASE_URL}/tasks/{task_id}"
        try:
            logger.debug(f"Querying status for task ID: {task_id}")
            response = requests.get(url, headers=self.headers, timeout=15) # 15 second timeout for status check
            response.raise_for_status()
            data = response.json()
            request_id = data.get("request_id")

            if "output" not in data:
                logger.error(f"Invalid response format from query API for task {task_id}: {data}")
                raise AlibabaVideoGeneratorError("Invalid response format from query API.", request_id=request_id)

            logger.debug(f"Received status for task {task_id}: {data['output'].get('task_status')}")
            return data # Return the full response dictionary

        except requests.exceptions.HTTPError as http_err:
            error_content = http_err.response.text
            logger.error(f"HTTP error occurred querying task {task_id}: {http_err} - {error_content}")
            try:
                error_data = http_err.response.json()
                error_code = error_data.get("code", f"HTTP_{http_err.response.status_code}")
                error_message = error_data.get("message", str(http_err))
                request_id = error_data.get("request_id")
                # Return a structured error if task failed at API level (e.g., 404 Not Found)
                # This allows the caller to distinguish between API errors and task failures
                return {
                    "request_id": request_id,
                    "output": {
                        "task_id": task_id,
                        "task_status": "API_ERROR",
                        "code": error_code,
                        "message": f"Failed to query task: {error_message}"
                    }
                }
            except ValueError:
                 return {
                    "request_id": None,
                    "output": {
                        "task_id": task_id,
                        "task_status": "API_ERROR",
                        "code": f"HTTP_{http_err.response.status_code}",
                        "message": f"Failed to query task: HTTP {http_err.response.status_code} - {error_content}"
                    }
                }

        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error occurred querying task {task_id}: {req_err}")
            # Indicate API error due to network/request issues
            return {
                "request_id": None,
                "output": {
                    "task_id": task_id,
                    "task_status": "API_ERROR",
                    "code": "NetworkError",
                    "message": f"Failed to query task due to network or request error: {req_err}"
                }
            }
        except Exception as e:
            logger.error(f"An unexpected error occurred querying task {task_id}: {e}", exc_info=True)
            return {
                "request_id": None,
                "output": {
                    "task_id": task_id,
                    "task_status": "API_ERROR",
                    "code": "UnexpectedError",
                    "message": f"An unexpected error occurred while querying task: {e}"
                }
            }

# Example Usage (requires DASHSCOPE_API_KEY env var set):
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        generator = AlibabaVideoGenerator()
        # Example: Create a task
        # task_id = generator.create_video_task(prompt="视频标题：走进三里屯，一场潮流与灵感的撞击。视频主题：在北京三里屯，以诗意视角邂逅年轻潮流与街头表达。1分钟沉浸式漫游，感受城市灵魂的跳跃。。视频结构：。开场部分：，time-lapse镜头：航拍北京城市天际线快速变幻，落日余晖映照高楼，镜头拉近切入三里屯SKP街口，街上人潮汹涌，一位穿搭时尚的人物背影走入画面，旁白：'这里是北京三里屯，此刻我正穿梭在这座城市最会穿搭的街头，带你看见年轻灵魂的碰撞与闪光。'。过渡镜头部分：，POV-shot镜头：第一人称视角掠过玻璃橱窗，映出亮眼服饰，随后手推开透明玻璃门进入一家潮牌店，门铃响起。正文段落部分：，潮流即态度场景：'这里的T恤不是流行，是态度；每一块印花，都是对规则的温柔反抗。在三里屯，穿什么不重要，穿'谁'才重要。'；街头即秀场场景：'你听，这是风在转弯的声音？每个人都像一首歌，走在街上就是开场白。在这里，连影子都有态度。'；咖啡馆即灵感站场景：'三里屯不只卖潮流，还泡灵感。在一杯Dirty的温度里，你会遇见刚刚好的自己。有些灵感，不用追，它会在咖啡香里慢慢靠近。'；深度洞察段场景：'年轻不等于喧哗，而是有勇气在城市的每一寸角落，写下属于自己的注解。'。结尾部分：，tracking-shot镜头：人物背影缓步走入华灯初上的人行街道中；镜头逐渐拉远，霓虹灯反射出五光十色；街角广告牌闪烁，人物突然转身，看向镜头轻轻一笑，旁白：'在三里屯，我找到了表达的自由和下一次出发的勇气。这里是____，我们下次在____见。")
        # print(f"Task submitted with ID: {task_id}")

        # Example: Query a task (replace with a real task ID)
        existing_task_id = "c744cf29-12e1-44a8-9467-610c4b8696e1"
        import time
        while True:
            result = generator.query_task_status(existing_task_id)
            status = result.get("output", {}).get("task_status")
            print(f"Task {existing_task_id} Status: {status}")
            if status in ["SUCCEEDED", "FAILED", "API_ERROR"]:
                print("Final Result:")
                print(result)
                break
            time.sleep(10) # Wait before querying again


    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except AlibabaVideoGeneratorError as api_err:
        print(f"API Error: {api_err}")
    except Exception as ex:
        print(f"An error occurred: {ex}")
