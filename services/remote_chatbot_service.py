"""
원격 GPU 서버 챗봇 서비스
GPU 서버의 chatbot API를 호출하여 LLM 응답 생성
"""
import requests
import os
from core.logger import setup_logger

logger = setup_logger(__name__)


class RemoteChatbotService:
    """원격 GPU 서버 챗봇 서비스"""

    def __init__(self):
        # 환경 변수에서 GPU 서버 URL 가져오기
        self.gpu_server_url = os.getenv('GPU_SERVER_URL', 'http://localhost:8000')
        self.api_key = os.getenv('GPU_API_KEY', '')
        logger.info(f"🌐 Remote Chatbot Service initialized: {self.gpu_server_url}")

    def generate_response(self, message, image=None):
        """
        원격 GPU 서버에서 챗봇 응답 생성

        Args:
            message: 사용자 메시지
            image: 이미지 파일 (선택사항)

        Returns:
            str: 챗봇 응답
        """
        try:
            # 요청 데이터 준비
            files = {}
            data = {'message': message}

            if image:
                # 이미지가 FileStorage 객체인 경우
                if hasattr(image, 'read'):
                    image.seek(0)  # 파일 포인터 초기화
                    files['image'] = (image.filename, image.read(), image.content_type)
                else:
                    # PIL Image 또는 파일 경로인 경우
                    files['image'] = image

            # 헤더 설정
            headers = {}
            if self.api_key:
                headers['X-API-Key'] = self.api_key

            logger.info(f"📡 Calling GPU chatbot server: {self.gpu_server_url}/api/v1/chatbot")

            # GPU 서버 API 호출
            response = requests.post(
                f"{self.gpu_server_url}/api/v1/chatbot",
                data=data,
                files=files if files else None,
                headers=headers,
                timeout=60  # LLM은 추론 시간이 길 수 있음
            )

            if response.status_code != 200:
                error_msg = response.json().get('message', 'Unknown error')
                raise Exception(f"GPU chatbot server error: {error_msg}")

            result = response.json()
            logger.info(f"✅ Chatbot response received from GPU server")

            return result['reply']

        except requests.exceptions.Timeout:
            logger.error("⏱️ GPU chatbot server timeout")
            return "죄송합니다. 응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."

        except requests.exceptions.ConnectionError:
            logger.error(f"🔌 GPU chatbot server connection failed: {self.gpu_server_url}")
            return "죄송합니다. 챗봇 서버에 연결할 수 없습니다."

        except Exception as e:
            logger.error(f"❌ Remote chatbot error: {e}")
            return f"죄송합니다. 오류가 발생했습니다: {str(e)}"


# 싱글톤 인스턴스
_remote_chatbot_service_instance = None


def get_remote_chatbot_service():
    """Remote Chatbot 서비스 싱글톤 인스턴스 반환"""
    global _remote_chatbot_service_instance
    if _remote_chatbot_service_instance is None:
        _remote_chatbot_service_instance = RemoteChatbotService()
    return _remote_chatbot_service_instance
