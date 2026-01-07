# MySkin Project - API 문서

## 🎯 개요
LED 마스크 스킨케어 애플리케이션의 백엔드 API 문서입니다.

**Base URL:** `http://localhost:5000`

---

## 📌 API 엔드포인트 목록

### 1. 피부 분석 (AI Analysis)

#### `POST /api/v1/analysis/face`
얼굴 이미지를 AI로 분석하여 부위별 점수와 LED 추천 솔루션을 반환합니다.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `file`: (File) 얼굴 이미지 (JPG, PNG)
  - `user_id`: (String, optional) 사용자 ID (기본값: 'anonymous')

**Response:**
```json
{
  "overall_score": 82,
  "timestamp": "2024-01-15T10:30:00",
  "regions": {
    "forehead": {
      "grade": 8,
      "raw_grade": 2,
      "score": 75,
      "details": [0.234, 0.456, ...],
      "metrics": {
        "주름_깊이": 23.4,
        "주름_밀도": 45.6,
        "색소침착": 12.3,
        ...
      }
    },
    "eye_l": { ... },
    "eye_r": { ... },
    "cheek_l": { ... },
    "cheek_r": { ... },
    "chin": { ... }
  },
  "recommendation": {
    "mode": "red",
    "duration": 20,
    "reason": "주름 및 탄력 개선 집중",
    "target_regions": ["forehead", "eye_l"],
    "intensity": 75,
    "ble_command": "START:RED:20",
    "issue_analysis": {
      "wrinkle": 45.2,
      "elasticity": 30.1,
      "pigmentation": 12.5,
      "acne": 5.0,
      "pore": 18.3
    }
  }
}
```

**특징:**
- 6개 부위별 독립 AI 모델 사용
- Regression 모델의 15~16개 세부 메트릭 제공
- AI 기반 LED 모드 자동 추천
- Seeed Xiao BLE 명령어 포함

---

### 2. 히스토리 관리

#### `POST /api/v1/history`
분석 결과를 히스토리에 저장합니다.

**Request:**
```json
{
  "user_id": "user_abc123",
  "overall_score": 82,
  "regions": { ... },
  "recommendation": { ... },
  "timestamp": "2024-01-15T10:30:00",
  "course_name": "AI 정밀 분석"
}
```

**Response:**
```json
{
  "success": true,
  "record_id": 1,
  "message": "히스토리가 저장되었습니다."
}
```

#### `GET /api/v1/history/<user_id>?limit=20`
사용자별 분석 히스토리를 조회합니다.

**Parameters:**
- `user_id` (path): 사용자 ID
- `limit` (query, optional): 최대 조회 개수 (기본값: 20)

**Response:**
```json
{
  "user_id": "user_abc123",
  "total_records": 15,
  "history": [
    {
      "id": 1,
      "user_id": "user_abc123",
      "timestamp": "2024-01-15T10:30:00",
      "overall_score": 82,
      "regions": { ... },
      "recommendation": { ... },
      "course_name": "AI 정밀 분석"
    },
    ...
  ]
}
```

---

### 3. 사용자 프로필

#### `POST /api/v1/user/profile`
사용자 프로필을 생성하거나 수정합니다.

**Request:**
```json
{
  "user_id": "user_abc123",
  "name": "김수지",
  "skin_type": "복합성",
  "concerns": ["주름", "색소침착", "모공"],
  "goals": "피부 탄력 개선 및 톤업"
}
```

**Response:**
```json
{
  "success": true,
  "profile": {
    "user_id": "user_abc123",
    "name": "김수지",
    "skin_type": "복합성",
    "concerns": ["주름", "색소침착", "모공"],
    "goals": "피부 탄력 개선 및 톤업",
    "created_at": "2024-01-10T09:00:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

#### `GET /api/v1/user/profile/<user_id>`
사용자 프로필을 조회합니다.

**Response:**
```json
{
  "user_id": "user_abc123",
  "profile": {
    "user_id": "user_abc123",
    "name": "김수지",
    "skin_type": "복합성",
    "concerns": ["주름", "색소침착", "모공"],
    "goals": "피부 탄력 개선 및 톤업",
    "created_at": "2024-01-10T09:00:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

---

### 4. 통계 및 분석

#### `GET /api/v1/stats/<user_id>`
사용자의 피부 변화 통계를 조회합니다.

**Response:**
```json
{
  "user_id": "user_abc123",
  "total_analyses": 15,
  "average_score": 78.5,
  "latest_score": 82,
  "best_score": 85,
  "trend": "improving",
  "improvement": 7.5,
  "recent_scores": [82, 80, 78, 75, 72, 70, 68],
  "region_stats": {
    "forehead": {
      "average": 75.2,
      "latest": 78,
      "best": 82
    },
    "eye_l": { ... },
    ...
  }
}
```

**필드 설명:**
- `trend`: "improving" (개선중) / "stable" (안정)
- `improvement`: 최신 점수 - 최초 점수 (양수면 개선)
- `recent_scores`: 최근 7개 기록

---

### 5. BLE 디바이스 설정 (Seeed Xiao BLE)

#### `GET /api/v1/device/config`
Seeed Xiao BLE 디바이스 설정을 반환합니다.

**Response:**
```json
{
  "device_name": "MySkin_LED_Mask",
  "ble_service_uuid": "0000ffe0-0000-1000-8000-00805f9b34fb",
  "supported_modes": ["red", "blue", "gold"],
  "pwm_range": [0, 255],
  "firmware_version": "1.0.0"
}
```

#### `GET /api/v1/device/modes`
사용 가능한 LED 모드 정보를 반환합니다.

**Response:**
```json
{
  "modes": {
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
  },
  "description": "각 LED 모드별 파장과 효과 정보"
}
```

---

## 🔧 데이터 저장 구조

### `data/history.json`
```json
[
  {
    "id": 1,
    "user_id": "user_abc123",
    "timestamp": "2024-01-15T10:30:00",
    "overall_score": 82,
    "regions": { ... },
    "recommendation": { ... },
    "course_name": "AI 정밀 분석"
  }
]
```

### `data/users.json`
```json
{
  "user_abc123": {
    "user_id": "user_abc123",
    "name": "김수지",
    "skin_type": "복합성",
    "concerns": ["주름", "색소침착"],
    "goals": "피부 탄력 개선",
    "created_at": "2024-01-10T09:00:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

---

## 🚀 향후 확장 계획

### Seeed Xiao BLE 통신
- **현재**: BLE 명령어 문자열 생성 (`START:RED:20`)
- **향후**:
  - WebBluetooth API를 통한 직접 제어
  - PWM 강도 조절 (0-255)
  - 실시간 센서 피드백 수신
  - 펌웨어 버전 체크 및 OTA 업데이트

### AI 모델 개선
- 실시간 부위별 세그멘테이션
- 시계열 분석 (피부 변화 예측)
- 개인화된 ML 추천 모델

### 데이터 저장
- SQLite 또는 PostgreSQL 마이그레이션
- 이미지 저장 및 비교 기능
- 클라우드 백업

---

## 📝 사용 예시

### Python (requests)
```python
import requests

# 1. 피부 분석
with open('face.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/v1/analysis/face',
        files={'file': f},
        data={'user_id': 'user_abc123'}
    )
result = response.json()

# 2. 히스토리 저장
requests.post(
    'http://localhost:5000/api/v1/history',
    json=result
)

# 3. 통계 조회
stats = requests.get('http://localhost:5000/api/v1/stats/user_abc123').json()
print(f"평균 점수: {stats['average_score']}")
```

### JavaScript (Fetch)
```javascript
// 피부 분석
const formData = new FormData();
formData.append('file', imageFile);
formData.append('user_id', 'user_abc123');

const response = await fetch('http://localhost:5000/api/v1/analysis/face', {
  method: 'POST',
  body: formData
});
const result = await response.json();

// LED 추천 확인
console.log(`추천 모드: ${result.recommendation.mode}`);
console.log(`BLE 명령: ${result.recommendation.ble_command}`);
```

---

## ⚙️ 설정 및 실행

```bash
# 의존성 설치
pip install flask torch torchvision pillow

# 서버 실행
python app.py

# 서버 주소
http://localhost:5000
```

---

## 📞 문의
프로젝트 관련 문의사항은 이슈로 등록해주세요.
