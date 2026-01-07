"""
피부 분석 오케스트레이션 서비스
"""
from services.ai_service import get_ai_service
from services.image_service import get_image_service
from services.metrics_service import MetricsService
from services.led_service import LEDService
from core.logger import setup_logger

logger = setup_logger(__name__)


class AnalysisService:
    """피부 분석 통합 서비스"""

    def __init__(self):
        self.ai_service = get_ai_service()
        self.image_service = get_image_service()
        self.metrics_service = MetricsService()
        self.led_service = LEDService()

    def analyze_face(self, pil_image, user_id="anonymous"):
        """
        전체 얼굴 분석

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
        logger.info(f"📸 [AI 분석 시작] 사용자: {user_id} | 이미지: {pil_image.size}")
        logger.info(f"{'='*50}")

        # 1. 이미지 유효성 검증
        is_valid, reason = self.image_service.validate_image(pil_image)
        if not is_valid:
            logger.error(f"❌ 이미지 검증 실패: {reason}")
            raise ValueError(reason)

        # 2. 이미지 전처리
        image_tensor = self.ai_service.preprocess_image(pil_image)

        # 3. 6개 부위 AI 분석
        logger.info("\n   🤖 [AI 분석 시작]")
        regions_data = {}
        total_score = 0
        zone_count = 0

        for zone in self.ai_service.models.keys():
            try:
                # AI 예측
                cls_out, reg_out = self.ai_service.predict(image_tensor, zone)

                # 메트릭 처리
                result = self.metrics_service.process_prediction(
                    cls_out, reg_out, zone
                )

                regions_data[zone] = result
                total_score += result["score"]
                zone_count += 1

                logger.info(f"   ✅ {zone}: Grade {result['grade']}, Score {result['score']:.1f}")

            except Exception as e:
                logger.error(f"   ❌ {zone} 분석 실패: {e}")

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
_analysis_service_instance = None


def get_analysis_service():
    """Analysis 서비스 싱글톤 인스턴스 반환"""
    global _analysis_service_instance
    if _analysis_service_instance is None:
        _analysis_service_instance = AnalysisService()
    return _analysis_service_instance
