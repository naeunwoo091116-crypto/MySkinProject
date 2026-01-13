import requests
import logging
import io
from PIL import Image
from core.config import GPU_SERVER_URL

logger = logging.getLogger(__name__)

class RemoteChatbotService:
    """원격 GPU 서버를 통한 챗봇 서비스"""

    def __init__(self):
        self.base_url = GPU_SERVER_URL.rstrip('/')
        logger.info(f"Using Remote Chatbot Service at {self.base_url}")

    def generate_response(self, message, image=None):
        try:
            data = {'message': message}
            files = {}

            if image:
                # Handle Image (can be file storage or PIL Image)
                img_byte_arr = io.BytesIO()
                
                if isinstance(image, Image.Image):
                    image.save(img_byte_arr, format='JPEG')
                else:
                    # If it's a FileStorage object from Flask
                    image.save(img_byte_arr)
                    img_byte_arr.seek(0)
                
                files['image'] = ('image.jpg', img_byte_arr.getvalue(), 'image/jpeg')

            logger.info("📡 Sending chatbot request to GPU server...")
            response = requests.post(
                f"{self.base_url}/api/v1/chatbot",
                data=data,
                files=files if files else None,
                timeout=300 # LLaVA 모델 응답 시간: 최대 5분
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result["reply"]
                else:
                    logger.error(f"Remote Chatbot Error: {result}")
                    return "죄송합니다. 원격 서버 오류가 발생했습니다."
            else:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return "죄송합니다. 서버 연결에 실패했습니다."

        except Exception as e:
            logger.error(f"❌ Remote chatbot request failed: {e}")
            import traceback
            traceback.print_exc()
            return "죄송합니다. 답변을 생성하는 도중 오류가 발생했습니다."

def get_remote_chatbot_service():
    return RemoteChatbotService()
