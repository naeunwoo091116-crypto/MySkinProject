"""
애플리케이션 설정
"""
import torch
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# PyTorch 디바이스 설정
DEVICE = torch.device('cpu')

# 데이터베이스 설정
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost/skin_analysis')

# AI 모델 설정
MODEL_CONFIGS = {
    "forehead": {
        "path": "models/forehead_model.pth",
        "num_classes": 4,
        "num_targets": 15
    },
    "eye_l": {
        "path": "models/left_eye_model.pth",
        "num_classes": 4,
        "num_targets": 8
    },
    "eye_r": {
        "path": "models/right_eye_model.pth",
        "num_classes": 4,
        "num_targets": 8
    },
    "cheek_l": {
        "path": "models/left_cheek_model.pth",
        "num_classes": 4,
        "num_targets": 16
    },
    "cheek_r": {
        "path": "models/right_cheek_model.pth",
        "num_classes": 4,
        "num_targets": 16
    },
    "chin": {
        "path": "models/chin_model.pth",
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
