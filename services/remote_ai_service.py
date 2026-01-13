import requests
import logging
import base64
import io
from PIL import Image
from core.config import GPU_SERVER_URL, MODEL_CONFIGS

logger = logging.getLogger(__name__)

class RemoteAIService:
    """원격 GPU 서버를 통한 AI 모델 추론 서비스"""

    def __init__(self):
        self.base_url = GPU_SERVER_URL.rstrip('/')
        self.models = MODEL_CONFIGS # AnalysisService에서 models.keys()를 순회할 때 필요함 (실제 모델은 로드하지 않음)
        logger.info(f"Using Remote AI Service at {self.base_url}")

    def predict_all_regions(self, pil_image):
        """
        원격 GPU 서버에 모든 부위 예측 요청
        """
        try:
            # 이미지 바이트 변환
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            files = {
                'file': ('image.jpg', img_byte_arr, 'image/jpeg')
            }

            logger.info("📡 Sending inference request to GPU server...")
            response = requests.post(f"{self.base_url}/api/v1/inference", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info("✅ Remote inference successful")
                    return result["predictions"]
                else:
                    raise Exception(f"GPU Server Error: {result}")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
            logger.error(f"❌ Remote inference failed: {e}")
            raise e

    def preprocess_image(self, pil_image):
        """AnalysisService 호환성 유지용 (원격에서는 사용 안 함)"""
        return None 

    def predict(self, *args, **kwargs):
        """AnalysisService 호환성 유지용 (에러 발생)"""
        raise NotImplementedError("Remote service primarily uses predict_all_regions")

# Singleton (Mocking get_ai_service behaviors if needed directly, though usually called via factory)
def get_remote_ai_service():
    return RemoteAIService()
