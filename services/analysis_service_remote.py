"""
원격 GPU 서버를 사용하는 피부 분석 서비스
analysis_service.py의 원격 버전
"""
from services.remote_ai_service import get_remote_ai_service
from services.image_service import get_image_service
from services.metrics_service import MetricsService
from services.led_service import LEDService
from core.logger import setup_logger

logger = setup_logger(__name__)


class RemoteAnalysisService:
    """원격 GPU 서버를 사용하는 피부 분석 통합 서비스"""

    def __init__(self):
        self.remote_ai = get_remote_ai_service()
        self.image_service = get_image_service()
        self.metrics_service = MetricsService()
        self.led_service = LEDService()

    def analyze_face(self, pil_image, user_id="anonymous"):
        """
        전체 얼굴 분석 (원격 GPU 서버 사용)

        Args:
            pil_image: PIL Image 객체
            user_id: 사용자 ID

        Returns:
            {
                "overall_score": float,
                "regions": {...},
                "recommendation": {...}
            }
        """
        logger.info(f"\n{'='*50}")
        logger.info(f"📸 [Remote AI 분석 시작] 사용자: {user_id} | 이미지: {pil_image.size}")
        logger.info(f"{'='*50}")

        # 1. 이미지 유효성 검증 (기본 검증만, MediaPipe 스킵)
        is_valid, reason = self.image_service.validate_image(pil_image, skip_face_detection=True)
        if not is_valid:
            logger.error(f"❌ 이미지 검증 실패: {reason}")
            raise ValueError(reason)

        # 2. 원격 GPU 서버에서 AI 분석
        logger.info("\n   🌐 [Remote GPU Server 호출]")
        predictions = self.remote_ai.predict_all_regions(pil_image)

        # 3. 예측 결과를 메트릭으로 변환
        regions_data = {}
        total_score = 0
        zone_count = 0

        for zone, pred in predictions.items():
            try:
                # 메트릭 처리
                result = self.metrics_service.process_prediction(
                    pred['cls_output'],
                    pred['reg_output'],
                    zone
                )

                regions_data[zone] = result
                total_score += result["score"]
                zone_count += 1

                logger.info(f"   ✅ {zone}: Grade {result['grade']}, Score {result['score']:.1f}")

            except Exception as e:
                logger.error(f"   ❌ {zone} 처리 실패: {e}")

        # 4. 전체 점수 계산
        overall_score = round(total_score / zone_count, 1) if zone_count > 0 else 0

        # 5. LED 추천
        analysis_result = {
            "overall_score": overall_score,
            "regions": regions_data
        }
        recommendation = self.led_service.recommend(analysis_result)

        logger.info(f"\n   📊 전체 점수: {overall_score}/100")
        logger.info(f"   💡 LED 추천: {recommendation['mode'].upper()} 모드 ({recommendation['duration']}분)")
        logger.info(f"{'='*50}\n")

        return {
            "overall_score": overall_score,
            "regions": regions_data,
            "recommendation": recommendation
        }


# 싱글톤 인스턴스
_remote_analysis_service_instance = None


def get_remote_analysis_service():
    """Remote Analysis 서비스 싱글톤 인스턴스 반환"""
    global _remote_analysis_service_instance
    if _remote_analysis_service_instance is None:
        _remote_analysis_service_instance = RemoteAnalysisService()
    return _remote_analysis_service_instance
