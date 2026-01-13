"""
원격 GPU 서버 AI 추론 서비스
GPU 서버의 inference API를 호출하여 AI 분석 수행
"""
import requests
import io
from PIL import Image
from core.logger import setup_logger
from core.config import METRIC_NAMES
import os

logger = setup_logger(__name__)


class RemoteAIService:
    """원격 GPU 서버 AI 서비스"""

    def __init__(self):
        # 환경 변수에서 GPU 서버 URL 가져오기
        self.gpu_server_url = os.getenv('GPU_SERVER_URL', 'http://localhost:8000')
        self.api_key = os.getenv('GPU_API_KEY', '')
        logger.info(f"🌐 Remote AI Service initialized: {self.gpu_server_url}")

    def predict_all_regions(self, pil_image):
        """
        원격 GPU 서버에서 모든 부위 분석

        Args:
            pil_image: PIL Image 객체

        Returns:
            dict: {zone: {cls_output, reg_output}}
        """
        try:
            # 이미지를 바이트로 변환
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)

            # GPU 서버 API 호출
            files = {'file': ('image.jpg', img_byte_arr, 'image/jpeg')}
            headers = {}
            if self.api_key:
                headers['X-API-Key'] = self.api_key

            logger.info(f"📡 Calling GPU server: {self.gpu_server_url}/api/v1/inference")
            response = requests.post(
                f"{self.gpu_server_url}/api/v1/inference",
                files=files,
                headers=headers,
                timeout=30
            )

            if response.status_code != 200:
                error_msg = response.json().get('message', 'Unknown error')
                raise Exception(f"GPU server error: {error_msg}")

            result = response.json()
            logger.info(f"✅ GPU inference completed on {result.get('device', 'unknown')}")

            return result['predictions']

        except requests.exceptions.Timeout:
            logger.error("⏱️ GPU server timeout")
            raise Exception("GPU 서버 응답 시간 초과")
        except requests.exceptions.ConnectionError:
            logger.error(f"🔌 GPU server connection failed: {self.gpu_server_url}")
            raise Exception(f"GPU 서버 연결 실패: {self.gpu_server_url}")
        except Exception as e:
            logger.error(f"❌ Remote AI inference error: {e}")
            raise

    def health_check(self):
        """GPU 서버 상태 확인"""
        try:
            response = requests.get(
                f"{self.gpu_server_url}/api/v1/health",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return {"status": "error", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# 싱글톤 인스턴스
_remote_ai_service_instance = None


def get_remote_ai_service():
    """Remote AI 서비스 싱글톤 인스턴스 반환"""
    global _remote_ai_service_instance
    if _remote_ai_service_instance is None:
        _remote_ai_service_instance = RemoteAIService()
    return _remote_ai_service_instance
