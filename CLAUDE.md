# MySkin Project

AI 기반 피부 분석 및 LED 테라피 추천 웹 애플리케이션

## Tech Stack

- **Backend**: Flask (Python 3.x)
- **Database**: PostgreSQL (primary) / SQLite (fallback)
- **ORM**: SQLAlchemy
- **AI/ML**: PyTorch, TorchVision, ResNet 기반 커스텀 모델
- **Image Processing**: Pillow (PIL), MediaPipe (얼굴 감지)
- **Frontend**: HTML/CSS/JavaScript (templates/index.html)

## Project Structure

```
MySkinProject/
├── app.py                  # Flask 앱 진입점, API 엔드포인트 정의
├── models/
│   ├── database.py         # SQLAlchemy 모델 (User, AnalysisHistory)
│   └── ai_models.py        # ResNetBalanced 모델 클래스
├── services/
│   ├── analysis_service.py # 분석 오케스트레이션 (메인 서비스)
│   ├── ai_service.py       # PyTorch 모델 로딩 및 예측
│   ├── image_service.py    # 이미지 검증/전처리
│   ├── led_service.py      # LED 모드 추천 엔진
│   ├── history_service.py  # 분석 히스토리 관리
│   └── metrics_service.py  # 점수/메트릭 계산
├── routes/                 # API 라우트 블루프린트
├── core/
│   ├── config.py           # 모델 경로, 메트릭 이름, 검증 설정
│   ├── constants.py        # LED 모드, 디바이스 설정, 임계값
│   └── logger.py           # 로깅 설정
├── utils/
│   └── decorators.py       # 유틸리티 데코레이터
├── templates/              # HTML 템플릿
├── data/                   # 데이터 파일
├── logs/                   # 로그 파일
└── venv1/                  # 가상환경 (무시)
```

## Running the Application

```bash
# 가상환경 활성화
venv1\Scripts\activate  # Windows
source venv1/bin/activate  # Linux/Mac

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

서버: `http://localhost:5001`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analysis/face` | 얼굴 이미지 분석 (multipart/form-data) |
| POST | `/api/v1/history` | 분석 결과 저장 |
| GET | `/api/v1/history/<user_id>` | 사용자 분석 히스토리 조회 |
| GET | `/api/v1/stats/<user_id>` | 사용자 통계 조회 |
| POST | `/api/v1/user/profile` | 사용자 프로필 저장/수정 |
| GET | `/api/v1/user/profile/<user_id>` | 사용자 프로필 조회 |
| GET | `/api/v1/users` | 전체 사용자 목록 |
| DELETE | `/api/v1/user/<user_id>` | 사용자 삭제 |
| GET | `/api/v1/device/config` | BLE 디바이스 설정 |
| GET | `/api/v1/device/modes` | LED 모드 정보 |

## Core Concepts

### 1. 6개 얼굴 부위 분석
- `forehead` (이마): 15개 메트릭
- `eye_l`, `eye_r` (눈가): 각 8개 메트릭
- `cheek_l`, `cheek_r` (볼): 각 16개 메트릭
- `chin` (턱): 15개 메트릭

### 2. AI 모델 구조
- 아키텍처: `ResNetBalanced` (Classification + Regression)
- 입력: 224x224 RGB 이미지
- 출력: 4-class 분류 + 부위별 회귀값
- 모델 파일: `models/*.pth`

### 3. LED 추천 로직
```python
# 문제 유형별 LED 모드
"acne", "pore" → "blue" (415nm)
"wrinkle", "elasticity" → "red" (630nm)
"pigmentation" → "gold" (590nm)
```

### 4. 점수 체계
- 전체 점수: 0-100 (부위별 평균)
- 등급: excellent(85+), good(70+), fair(50+), poor(<50)

## Database Schema

### Users 테이블
```python
user_id: String (unique)
name: String
skin_type: String
concerns: JSON  # ["주름", "색소침착", "모공"]
goals: Text
```

### AnalysisHistory 테이블
```python
user_id: String
timestamp: DateTime
overall_score: Integer
regions: JSON  # 전체 분석 데이터
recommendation: JSON  # LED 추천
```

## Development Guidelines

### 코드 패턴
1. **싱글톤 서비스**: `get_*_service()` 함수로 인스턴스 획득
2. **에러 처리**: ValueError로 이미지 검증 실패 처리
3. **로깅**: `core.logger.setup_logger(__name__)` 사용

### 새 서비스 추가 시
```python
class NewService:
    def __init__(self):
        pass

_instance = None

def get_new_service():
    global _instance
    if _instance is None:
        _instance = NewService()
    return _instance
```

### 새 API 엔드포인트 추가 시
1. `routes/` 디렉토리에 블루프린트 생성
2. `app.py`에서 블루프린트 등록

### 이미지 검증 설정 (core/config.py)
- 최소 크기: 100px
- 밝기 범위: 20-235
- MediaPipe 감지 신뢰도: 0.5

## Environment Variables (.env)

```
DATABASE_URL=postgresql://postgres:myskin123@localhost:5432/myskin
```

## BLE 디바이스 통합

- 디바이스: Seeed Xiao BLE
- 서비스 UUID: `0000ffe0-0000-1000-8000-00805f9b34fb`
- 명령 형식: `START:{MODE}:{DURATION}`
  - 예: `START:RED:20`

## Testing

```bash
# 분석 API 테스트
curl -X POST http://localhost:5001/api/v1/analysis/face \
  -F "file=@test_image.jpg" \
  -F "user_id=test_user"

# 히스토리 조회
curl http://localhost:5001/api/v1/history/test_user
```

## Notes

- 한국어 UI 메시지 및 로그 사용
- SQLite 폴백으로 PostgreSQL 없이도 동작
- 모델 파일(.pth)은 버전 관리에서 제외 권장
