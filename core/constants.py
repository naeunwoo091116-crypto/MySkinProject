"""
애플리케이션 상수
"""

# LED 모드 정의
LED_MODES = {
    "red": {
        "wavelength": 630,
        "benefits": ["주름개선", "탄력증진", "콜라겐생성"],
        "target_issues": ["wrinkle", "elasticity", "sagging"]
    },
    "blue": {
        "wavelength": 415,
        "benefits": ["여드름완화", "모공진정", "피지조절"],
        "target_issues": ["acne", "pore", "sebum", "redness"]
    },
    "gold": {
        "wavelength": 590,
        "benefits": ["미백", "색소완화", "피부톤개선"],
        "target_issues": ["pigmentation", "tone", "dark_spot"]
    }
}

# Seeed Xiao BLE 디바이스 설정
DEVICE_CONFIG = {
    "device_name": "MySkin_LED_Mask",
    "ble_service_uuid": "0000ffe0-0000-1000-8000-00805f9b34fb",
    "supported_modes": ["red", "blue", "gold"],
    "pwm_range": [0, 255],
    "firmware_version": "1.0.0"
}

# 점수 계산 파라미터
SCORE_THRESHOLDS = {
    "excellent": 85,
    "good": 70,
    "fair": 50,
    "poor": 0
}

# LED 추천 파라미터
LED_DURATION_THRESHOLDS = {
    "high_severity": (40, 25),    # (severity, duration_minutes)
    "medium_severity": (25, 20),
    "low_severity": (0, 15)
}

# 히스토리 조회 제한
MAX_HISTORY_ITEMS = 20
