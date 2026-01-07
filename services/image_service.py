"""
이미지 전처리 및 검증 서비스 (MediaPipe 얼굴 검출 포함)
"""
import numpy as np
from PIL import Image
from core.config import MIN_IMAGE_SIZE, MIN_BRIGHTNESS, MAX_BRIGHTNESS
from core.logger import setup_logger

logger = setup_logger(__name__)


class ImageService:
    """이미지 검증 및 전처리 서비스"""

    def __init__(self):
        self.face_detector = None

    def _get_face_detector(self):
        """Face Detector 인스턴스 반환 (OpenCV)"""
        if self.face_detector is not None:
            return self.face_detector

        try:
            # OpenCV import
            import cv2
            
            # Haar Cascade 로드
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_detector = cv2.CascadeClassifier(cascade_path)
            
            logger.info("✅ OpenCV Face Detector 초기화 완료")
            return self.face_detector

        except Exception as e:
            logger.error(f"❌ Face Detector 초기화 실패: {e}")
            return None

    def validate_image(self, pil_image):
        """
        이미지 유효성 검증 (엄격한 얼굴 인식)
        """
        logger.info("\n   🔍 [이미지 검증 시작]")

        try:
            # 1. 이미지 크기 확인
            width, height = pil_image.size
            logger.info(f"   📏 이미지 크기: {width}x{height}")

            if width < MIN_IMAGE_SIZE or height < MIN_IMAGE_SIZE:
                return False, f"이미지가 너무 작습니다 (최소 {MIN_IMAGE_SIZE}x{MIN_IMAGE_SIZE})"

            # 2. 이미지를 numpy 배열로 변환
            img_array = np.array(pil_image, dtype=np.uint8)

            # 3. 밝기 확인
            mean_brightness = np.mean(img_array)
            logger.info(f"   💡 평균 밝기: {mean_brightness:.1f}")

            if mean_brightness < MIN_BRIGHTNESS:
                return False, "이미지가 너무 어둡습니다"
            if mean_brightness > MAX_BRIGHTNESS:
                return False, "이미지가 너무 밝습니다"

            # 4. 얼굴 검출 (OpenCV 엄격 모드)
            detector = self._get_face_detector()
            
            if detector is None:
                 logger.error("   ❌ Face Detector를 로드할 수 없습니다.")
                 return False, "서버 내부 오류: 얼굴 인식 모델을 로드할 수 없습니다."

            logger.info("   🤖 얼굴 검출 실행 중 (OpenCV)...")
            
            # Grayscale 변환
            import cv2
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # 얼굴 검출
            faces = detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            if len(faces) == 0:
                logger.warning("   ❌ 얼굴이 감지되지 않았습니다")
                return False, "얼굴이 감지되지 않았습니다. 정면 사진을 사용해주세요."

            num_faces = len(faces)
            logger.info(f"   ✅ {num_faces}개의 얼굴 감지")

            if num_faces > 1:
                logger.warning(f"   ⚠️ 여러 얼굴({num_faces}개)이 감지되었습니다. 중앙에 위치한 얼굴을 기준으로 분석합니다.")

            logger.info("   ✅ 이미지 검증 통과")
            return True, "OK"

        except Exception as e:
            logger.error(f"❌ 이미지 검증 오류: {e}")
            import traceback
            traceback.print_exc()
            return False, f"이미지 검증 중 오류가 발생했습니다: {str(e)}"


# 싱글톤 인스턴스
_image_service_instance = None


def get_image_service():
    """Image 서비스 싱글톤 인스턴스 반환"""
    global _image_service_instance
    if _image_service_instance is None:
        _image_service_instance = ImageService()
    return _image_service_instance
