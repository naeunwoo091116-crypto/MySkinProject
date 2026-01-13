"""
메트릭 변환 및 점수 계산 서비스
"""
import torch
from core.config import METRIC_NAMES
from core.logger import setup_logger

logger = setup_logger(__name__)


class MetricsService:
    """메트릭 변환 및 점수 계산"""

    @staticmethod
    def parse_regression_values(region_name, reg_values):
        """
        Regression 값을 의미 있는 딕셔너리로 변환

        모델 출력 범위에 따라 적응형 정규화 적용:
        - 매우 작은 값(0-1 범위): 100배 스케일링
        - 중간 값(0-10 범위): 10배 스케일링
        - 큰 값(그 이상): 그대로 사용

        Args:
            region_name: 부위 이름
            reg_values: 회귀 값 리스트

        Returns:
            dict: {metric_name: value}
        """
        metrics = METRIC_NAMES.get(region_name, [])
        parsed = {}

        # 전체 값의 범위 확인
        if reg_values:
            max_val = max(abs(v) for v in reg_values)

            # 적응형 스케일 팩터 결정
            if max_val < 0.1:
                scale_factor = 1000  # 매우 작은 값 (0~0.1 범위)
            elif max_val < 1:
                scale_factor = 100   # 작은 값 (0.1~1 범위)
            elif max_val < 10:
                scale_factor = 10    # 중간 값 (1~10 범위)
            else:
                scale_factor = 1     # 이미 적절한 범위

        for i, metric_name in enumerate(metrics):
            if i < len(reg_values):
                # 적응형 스케일링 적용
                raw_value = reg_values[i]
                normalized = max(0, min(100, abs(raw_value) * scale_factor))
                parsed[metric_name] = round(normalized, 1)  # 소수점 1자리

        return parsed

    @staticmethod
    def calculate_score(grade, metrics, max_grade=4):
        """
        부위별 점수 계산

        Args:
            grade: 분류 등급 (0-3)
            metrics: 메트릭 딕셔너리
            max_grade: 최대 등급

        Returns:
            float: 0-100 점수
        """
        # 기본 점수 (등급 기반)
        # Grade 0 (좋음) -> 100점 시작
        # Grade 3 (나쁨) -> 40점 시작 (등급당 20점 감점)
        base_score = 100 - (grade * 20)

        # 메트릭 기반 조정 (상위 5개 메트릭의 평균)
        # 메트릭 값(0-100)이 높을수록(결함이 많을수록) 점수 차감
        if metrics:
            sorted_metrics = sorted(metrics.values(), reverse=True)
            top5 = sorted_metrics[:5]
            avg_metric = sum(top5) / len(top5) if top5 else 0

            # 메트릭 수치의 30%만큼 추가 감점
            deduction = avg_metric * 0.3
            final_score = base_score - deduction
        else:
            final_score = base_score

        # 0-100 범위로 클리핑
        return max(10, min(100, final_score))

    @staticmethod
    def process_prediction(cls_out, reg_out, region_name):
        """
        AI 예측 결과 처리

        Args:
            cls_out: 분류 출력 (Tensor 또는 list)
            reg_out: 회귀 출력 (Tensor 또는 list)
            region_name: 부위 이름

        Returns:
            dict: {grade, metrics, score}
        """
        # 분류 결과 (Tensor 또는 list 처리)
        if isinstance(cls_out, list):
            # 원격 GPU 서버에서 받은 list 데이터
            cls_tensor = torch.tensor(cls_out)
            grade = torch.argmax(cls_tensor, dim=1).item()
            confidence = torch.softmax(cls_tensor, dim=1).max().item()
        else:
            # 로컬 Tensor 데이터
            grade = torch.argmax(cls_out, dim=1).item()
            confidence = torch.softmax(cls_out, dim=1).max().item()

        # 회귀 결과 (Tensor 또는 list 처리)
        if isinstance(reg_out, list):
            # 원격 GPU 서버에서 받은 list 데이터
            reg_values = reg_out[0] if isinstance(reg_out[0], list) else reg_out
        else:
            # 로컬 Tensor 데이터
            reg_values = reg_out.squeeze().cpu().numpy().tolist()

        metrics = MetricsService.parse_regression_values(region_name, reg_values)

        # 점수 계산
        score = MetricsService.calculate_score(grade, metrics)

        return {
            "grade": int(grade),
            "confidence": round(confidence * 100, 1),
            "metrics": metrics,
            "score": round(score, 1)
        }
