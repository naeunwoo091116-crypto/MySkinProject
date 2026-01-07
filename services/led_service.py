"""
LED 추천 엔진 서비스
"""
from core.constants import LED_MODES, DEVICE_CONFIG, LED_DURATION_THRESHOLDS
from core.logger import setup_logger

logger = setup_logger(__name__)


class LEDService:
    """LED 모드 추천 서비스"""

    @staticmethod
    def recommend(analysis_results):
        """
        피부 분석 결과를 기반으로 최적의 LED 모드 추천

        Args:
            analysis_results: {"overall_score": int, "regions": {...}}

        Returns:
            {
                "mode": "red/blue/gold",
                "duration": int (분),
                "reason": str,
                "target_regions": [str],
                "intensity": int (0-100),
                "ble_command": str
            }
        """
        regions = analysis_results.get("regions", {})
        overall_score = analysis_results.get("overall_score", 75)

        # 1. 부위별 문제 점수 집계
        issue_scores = {
            "wrinkle": 0,
            "elasticity": 0,
            "pigmentation": 0,
            "acne": 0,
            "pore": 0
        }

        weak_regions = []

        for region_name, data in regions.items():
            score = data.get("score", 75)
            if score < 70:
                weak_regions.append(region_name)

            # 부위별 특성에 따라 문제 유형 가중치 부여
            if region_name in ["forehead", "eye_l", "eye_r"]:
                issue_scores["wrinkle"] += (100 - score) * 0.3
                issue_scores["elasticity"] += (100 - score) * 0.2
            elif region_name in ["cheek_l", "cheek_r"]:
                issue_scores["pore"] += (100 - score) * 0.25
                issue_scores["pigmentation"] += (100 - score) * 0.2
            elif region_name == "chin":
                issue_scores["acne"] += (100 - score) * 0.3

        # 2. 가장 심각한 문제 찾기
        main_issue = max(issue_scores, key=issue_scores.get)
        issue_severity = issue_scores[main_issue]

        # 3. LED 모드 선택
        if main_issue in ["acne", "pore"]:
            mode = "blue"
            reason = "모공 및 피지 문제 집중 케어"
        elif main_issue in ["wrinkle", "elasticity"]:
            mode = "red"
            reason = "주름 및 탄력 개선 집중"
        else:
            mode = "gold"
            reason = "색소 침착 및 피부톤 개선"

        # 4. 시간 조정 (문제가 심각할수록 길게)
        if issue_severity > 40:
            duration = 25
        elif issue_severity > 25:
            duration = 20
        else:
            duration = 15

        # 5. 강도 계산 (향후 BLE PWM 제어용)
        intensity = min(100, max(50, int(issue_severity * 1.5)))

        return {
            "mode": mode,
            "duration": duration,
            "reason": reason,
            "target_regions": weak_regions,
            "intensity": intensity,
            "ble_command": f"START:{mode.upper()}:{duration}",
            "issue_analysis": {k: round(v, 2) for k, v in issue_scores.items()}
        }

    @staticmethod
    def get_device_config():
        """
        Seeed Xiao BLE 디바이스 설정 반환

        Returns:
            dict: 디바이스 설정
        """
        return DEVICE_CONFIG

    @staticmethod
    def get_led_modes():
        """
        지원하는 LED 모드 정보 반환

        Returns:
            dict: LED 모드 정보
        """
        return LED_MODES
