"""
이미지 전처리 및 검증 서비스 (MediaPipe 얼굴 검출)
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
        """Face Detector 인스턴스 반환 (MediaPipe)"""
        if self.face_detector is not None:
            return self.face_detector

        try:
            # MediaPipe Face Detection (v0.10.x 새 API)
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision

            # BaseOptions 설정
            base_options = python.BaseOptions(model_asset_path='detector.tflite')
            options = vision.FaceDetectorOptions(
                base_options=base_options,
                min_detection_confidence=0.7
            )
            self.face_detector = vision.FaceDetector.create_from_options(options)

            logger.info("✅ MediaPipe Face Detector 초기화 완료")
            return self.face_detector

        except Exception as e:
            logger.error(f"❌ Face Detector 초기화 실패: {e}")
            logger.error("   MediaPipe 모델 파일이 필요합니다. detector.tflite 파일을 다운로드해주세요.")
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

            # 4. 얼굴 검출 (MediaPipe)
            detector = self._get_face_detector()

            if detector is None:
                 logger.error("   ❌ Face Detector를 로드할 수 없습니다.")
                 return False, "서버 내부 오류: 얼굴 인식 모델을 로드할 수 없습니다."

            logger.info("   🤖 얼굴 검출 실행 중 (MediaPipe)...")

            # MediaPipe v0.10.x는 Image 객체 필요
            import mediapipe as mp

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_array)
            detection_result = detector.detect(mp_image)

            if not detection_result.detections:
                logger.warning("   ❌ 얼굴이 감지되지 않았습니다")
                return False, "얼굴이 감지되지 않았습니다. 정면 사진을 사용해주세요."

            num_faces = len(detection_result.detections)
            logger.info(f"   ✅ {num_faces}개의 얼굴 감지")

            # 신뢰도 정보 출력
            for i, detection in enumerate(detection_result.detections):
                for category in detection.categories:
                    confidence = category.score
                    logger.info(f"   📊 얼굴 #{i+1} 신뢰도: {confidence:.2%}")

            # 여러 얼굴이 감지된 경우 경고
            if num_faces > 1:
                logger.warning(f"   ⚠️ {num_faces}명의 얼굴이 감지되었습니다. 한 명만 나온 사진을 권장합니다.")
                # 가장 신뢰도 높은 얼굴 선택
                best_detection = max(detection_result.detections,
                                    key=lambda d: max(cat.score for cat in d.categories))
                best_confidence = max(cat.score for cat in best_detection.categories)
                logger.info(f"   📍 가장 신뢰도 높은 얼굴 선택: {best_confidence:.2%}")

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
