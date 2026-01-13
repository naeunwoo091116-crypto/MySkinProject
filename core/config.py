"""
애플리케이션 설정
"""
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# PyTorch 디바이스 설정 (GPU 서버에서만 사용)
try:
    import torch
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
except ImportError:
    # torch가 없는 환경 (Render 등)에서는 None으로 설정
    DEVICE = None

# 데이터베이스 설정
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost/skin_analysis')

# 프로젝트 루트 디렉토리 (절대 경로 계산)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# AI 모델 설정 (절대 경로 사용)
MODEL_CONFIGS = {
    "forehead": {
        "path": os.path.join(BASE_DIR, "models/forehead_model.pth"),
        "num_classes": 4,
        "num_targets": 15
    },
    "eye_l": {
        "path": os.path.join(BASE_DIR, "models/left_eye_model.pth"),
        "num_classes": 4,
        "num_targets": 8
    },
    "eye_r": {
        "path": os.path.join(BASE_DIR, "models/right_eye_model.pth"),
        "num_classes": 4,
        "num_targets": 8
    },
    "cheek_l": {
        "path": os.path.join(BASE_DIR, "models/left_cheek_model.pth"),
        "num_classes": 4,
        "num_targets": 16
    },
    "cheek_r": {
        "path": os.path.join(BASE_DIR, "models/right_cheek_model.pth"),
        "num_classes": 4,
        "num_targets": 16
    },
    "chin": {
        "path": os.path.join(BASE_DIR, "models/chin_model.pth"),
        "num_classes": 4,
        "num_targets": 15
    }
}

# 부위별 메트릭 이름
METRIC_NAMES = {
    "forehead": [
        "wrinkle_depth", "elasticity", "hydration", "pigmentation",
        "redness", "pore_size", "sebum", "texture", "firmness",
        "smoothness", "radiance", "evenness", "fine_lines",
        "deep_wrinkles", "sagging"
    ],
    "eye_l": [
        "wrinkle_depth", "dark_circles", "puffiness", "elasticity",
        "fine_lines", "hydration", "firmness", "crow_feet"
    ],
    "eye_r": [
        "wrinkle_depth", "dark_circles", "puffiness", "elasticity",
        "fine_lines", "hydration", "firmness", "crow_feet"
    ],
    "cheek_l": [
        "wrinkle_depth", "elasticity", "hydration", "pigmentation",
        "redness", "pore_size", "sebum", "texture", "firmness",
        "smoothness", "radiance", "evenness", "acne", "scars",
        "capillaries", "sagging"
    ],
    "cheek_r": [
        "wrinkle_depth", "elasticity", "hydration", "pigmentation",
        "redness", "pore_size", "sebum", "texture", "firmness",
        "smoothness", "radiance", "evenness", "acne", "scars",
        "capillaries", "sagging"
    ],
    "chin": [
        "wrinkle_depth", "elasticity", "hydration", "pigmentation",
        "redness", "pore_size", "sebum", "texture", "firmness",
        "smoothness", "acne", "scars", "oiliness", "roughness",
        "sagging"
    ]
}

# 이미지 검증 설정
MIN_IMAGE_SIZE = 100  # 최소 이미지 크기 (px)
MIN_BRIGHTNESS = 20   # 최소 밝기
MAX_BRIGHTNESS = 235  # 최대 밝기

# MediaPipe 설정
MEDIAPIPE_MIN_DETECTION_CONFIDENCE = 0.5
MEDIAPIPE_MODEL_SELECTION = 1  # 0: 2m 이내, 1: 5m 이내 (더 정확)
