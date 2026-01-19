import numpy as np
from PIL import Image
from core.config import MIN_IMAGE_SIZE, MIN_BRIGHTNESS, MAX_BRIGHTNESS
from core.logger import setup_logger

logger = setup_logger(__name__)

class ImageService:
    def __init__(self):
        self.face_detector = None

    def _get_face_detector(self):
        if self.face_detector is not None:
            return self.face_detector
        
        try:
            # 실행 시점에 임포트하여 AttributeError 방지
            import mediapipe as mp
            mp_face_detection = mp.solutions.face_detection
            
            self.face_detector = mp_face_detection.FaceDetection(
                model_selection=1,
                min_detection_confidence=0.7
            )
            logger.info("✅ MediaPipe Face Detector 초기화 완료")
            return self.face_detector
        except Exception as e:
            logger.error(f"❌ Face Detector 초기화 실패: {e}")
            return None

    def validate_image(self, pil_image, skip_face_detection=False):
        try:
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            img_array = np.array(pil_image)

            if skip_face_detection:
                return True, "OK"

            detector = self._get_face_detector()
            if detector is None:
                 return False, "얼굴 인식 모델 로드 실패"

            results = detector.process(img_array)
            if not results or not results.detections:
                return False, "얼굴이 감지되지 않았습니다."

            return True, "OK"
        except Exception as e:
            return False, f"검증 오류: {str(e)}"

_image_service_instance = None
def get_image_service():
    global _image_service_instance
    if _image_service_instance is None:
        _image_service_instance = ImageService()
    return _image_service_instance