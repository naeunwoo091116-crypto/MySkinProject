"""
AI 모델 로딩 및 예측 서비스
"""
import torch
from torchvision import transforms
from core.config import MODEL_CONFIGS, DEVICE
from core.logger import setup_logger
from models.ai_models import ResNetBalanced
import os

logger = setup_logger(__name__)


class AIModelService:
    """AI 모델 관리 서비스"""

    def __init__(self):
        self.models = {}
        self.device = DEVICE
        self.transform = self._create_transform()
        self.load_models()

    def _create_transform(self):
        """이미지 전처리 transform 생성"""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def load_models(self):
        """6개 부위 모델 로딩"""
        logger.info("--- AI 모델 로딩 시작 ---")

        for region_name, config in MODEL_CONFIGS.items():
            path = config["path"]
            n_cls = config["num_classes"]
            n_reg = config["num_targets"]

            try:
                if os.path.exists(path):
                    logger.info(f"🔄 로딩 중: {region_name} (Class:{n_cls}, Reg:{n_reg})")

                    # 각 부위에 맞는 파라미터로 모델 생성
                    model = ResNetBalanced(
                        num_classes=n_cls,
                        num_regression_targets=n_reg
                    )

                    # 가중치 로드
                    checkpoint = torch.load(path, map_location=self.device)

                    if isinstance(checkpoint, dict):
                        if 'state_dict' in checkpoint:
                            state_dict = checkpoint['state_dict']
                        elif 'model' in checkpoint:
                            state_dict = checkpoint['model']
                        else:
                            state_dict = checkpoint
                    else:
                        state_dict = checkpoint

                    model.load_state_dict(state_dict)
                    model.eval()  # 평가 모드
                    model.to(self.device)

                    self.models[region_name] = model
                    logger.info(f"✅ {region_name} 로드 성공!")
                else:
                    logger.error(f"❌ 파일 없음: {path}")

            except Exception as e:
                logger.error(f"⚠️ {region_name} 로드 실패: {e}")
                logger.error(f"-> 설정값(num_classes={n_cls}, targets={n_reg})이 .pth 파일과 맞는지 확인하세요.")

        logger.info(f"총 {len(self.models)}개 모델 로드 완료")

    def predict(self, image_tensor, zone):
        """
        특정 부위 예측

        Args:
            image_tensor: 전처리된 이미지 텐서
            zone: 부위 이름 (forehead, eye_l, etc.)

        Returns:
            (classification_output, regression_output)
        """
        if zone not in self.models:
            raise ValueError(f"모델을 찾을 수 없습니다: {zone}")

        model = self.models[zone]

        with torch.no_grad():
            cls_out, reg_out = model(image_tensor.to(self.device))

        return cls_out, reg_out

    def predict_all_zones(self, image_tensor):
        """
        모든 부위 예측

        Args:
            image_tensor: 전처리된 이미지 텐서

        Returns:
            dict: {zone: (cls_out, reg_out)}
        """
        results = {}

        for zone in self.models.keys():
            results[zone] = self.predict(image_tensor, zone)

        return results

    def preprocess_image(self, pil_image):
        """
        PIL 이미지를 텐서로 변환

        Args:
            pil_image: PIL Image 객체

        Returns:
            torch.Tensor: 전처리된 이미지 텐서
        """
        return self.transform(pil_image).unsqueeze(0)

    def predict_all_regions(self, pil_image):
        """
        PIL 이미지로 모든 부위 예측 (GPU 서버 API용)

        Args:
            pil_image: PIL Image 객체

        Returns:
            dict: {zone: {"cls_output": [...], "reg_output": [...]}}
        """
        # 이미지 전처리
        image_tensor = self.preprocess_image(pil_image)

        results = {}
        for zone in self.models.keys():
            cls_out, reg_out = self.predict(image_tensor, zone)

            # 텐서를 리스트로 변환 (JSON 직렬화 가능하도록)
            results[zone] = {
                "cls_output": cls_out.cpu().numpy().tolist(),
                "reg_output": reg_out.cpu().numpy().tolist()
            }

        return results


# 싱글톤 인스턴스
_ai_service_instance = None


def get_ai_service():
    """AI 서비스 싱글톤 인스턴스 반환"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIModelService()
    return _ai_service_instance
