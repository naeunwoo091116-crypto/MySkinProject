# 📦 MySkin 프로젝트 배포 요약

## 🏗️ 최종 배포 구조

```
┌──────────────────────────────────────────────────────────┐
│                   사용자 (웹 브라우저)                      │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│  Render (무료) - https://myskin-web.onrender.com         │
│  ────────────────────────────────────────────────────    │
│  • Flask 웹 서버 (app_render.py)                         │
│  • 프론트엔드 (HTML/CSS/JS)                               │
│  • PostgreSQL 데이터베이스 (사용자, 히스토리)                │
│  • 이미지 검증 (얼굴 감지)                                  │
│  • LED 추천 로직                                          │
└────────────┬────────────────────────┬────────────────────┘
             │                        │
             │ API 호출               │ API 호출
             ▼                        ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│  GPU 서버 (별도)         │ │  GPU 서버 (별도)         │
│  /api/v1/inference      │ │  /api/v1/chatbot        │
│  ──────────────────     │ │  ──────────────────     │
│  • PyTorch ResNet       │ │  • LLaVA 1.5 7B         │
│  • 6개 부위 분석 모델    │ │  • 피부 상담 챗봇        │
│  • CUDA 가속            │ │  • 이미지+텍스트 처리    │
└─────────────────────────┘ └─────────────────────────┘
```

---

## 💰 비용 구조

| 구성 요소 | 호스팅 | 비용 | 설명 |
|---------|-------|------|------|
| **웹 서버** | Render Free | $0/월 | Flask 앱, 프론트엔드, DB |
| **PostgreSQL** | Render Free | $0/월 | 1GB 저장공간 |
| **GPU 서버** | 자체 운영 | - | AI 추론 전용 (본인 서버) |
| **총 비용** | | **$0/월** | 완전 무료 |

---

## 📁 파일 구조

### Render 배포용 (GitHub에 업로드)
```
MySkinProject/
├── app_render.py              # Render용 Flask 앱 (원격 AI 사용)
├── requirements_render.txt    # Render 의존성 (torch 제외)
├── build.sh                   # Render 빌드 스크립트
├── .gitignore                 # Git 제외 파일 목록
├── templates/                 # HTML 템플릿
├── models/database.py         # DB 모델 (Cloud SQL 지원)
├── services/
│   ├── remote_ai_service.py      # GPU 서버 AI 호출
│   ├── remote_chatbot_service.py # GPU 서버 챗봇 호출
│   ├── analysis_service_remote.py
│   ├── image_service.py
│   ├── led_service.py
│   └── history_service.py
└── FREE_DEPLOYMENT.md         # 무료 배포 가이드

```

### GPU 서버 배포용 (별도 서버에 업로드)
```
MySkinProject/
├── gpu_server/
│   ├── inference_api.py       # GPU API 서버
│   ├── requirements.txt       # GPU 서버 의존성
│   └── README.md              # GPU 서버 배포 가이드
├── models/
│   ├── *.pth                  # PyTorch 모델 파일 (6개)
│   └── ai_models.py
├── final/                     # LLaVA LoRA 어댑터
├── services/
│   ├── ai_service.py          # PyTorch 추론
│   ├── chatbot_service.py     # LLaVA 챗봇
│   └── image_service.py
└── core/
    ├── config.py
    ├── constants.py
    └── logger.py
```

---

## 🚀 배포 절차 (3단계)

### ✅ Step 1: GitHub에 코드 업로드 (5분)

```bash
cd C:\Users\user\Downloads\MySkinProject

git init
git add .
git commit -m "Initial commit - MySkin project"

# GitHub 리포지토리 생성 후
git remote add origin https://github.com/YOUR_USERNAME/MySkinProject.git
git push -u origin main
```

### ✅ Step 2: Render 무료 배포 (10분)

1. **https://render.com** 가입 (GitHub 연동)
2. **PostgreSQL 생성**:
   - New > PostgreSQL
   - Name: `myskin-db`
   - Plan: **Free**
3. **Web Service 생성**:
   - New > Web Service
   - GitHub 리포지토리 연결
   - Name: `myskin-web`
   - Build: `./build.sh`
   - Start: `gunicorn -b 0.0.0.0:$PORT app_render:app --workers 2`
   - Plan: **Free**
4. **환경 변수 설정**:
   - `DATABASE_URL`: (PostgreSQL 연결 URL)
   - `GPU_SERVER_URL`: `http://YOUR_GPU_IP:8000` (나중에 설정)

**배포 완료 URL**: `https://myskin-web.onrender.com`

### ✅ Step 3: GPU 서버 설정 (15분)

```bash
# GPU 서버에 파일 업로드
scp -r MySkinProject username@gpu-server:/home/username/

# SSH 접속
ssh username@gpu-server

# 설치 및 실행
cd MySkinProject/gpu_server
pip install -r requirements.txt
nohup python inference_api.py > inference.log 2>&1 &

# 방화벽 포트 열기
sudo ufw allow 8000

# 공인 IP 확인
curl ifconfig.me
```

**Render에 GPU 서버 URL 등록**:
- Render > myskin-web > Environment
- `GPU_SERVER_URL` = `http://YOUR_GPU_IP:8000`

---

## 🔧 환경 변수 설정

### Render (웹 서버)
| 변수명 | 값 | 설명 |
|-------|-----|------|
| `PYTHON_VERSION` | `3.11.0` | Python 버전 |
| `DATABASE_URL` | (자동 생성) | PostgreSQL 연결 |
| `GPU_SERVER_URL` | `http://YOUR_GPU_IP:8000` | GPU 서버 주소 |
| `GPU_API_KEY` | (선택사항) | API 보안 키 |

### GPU 서버
| 변수명 | 값 | 설명 |
|-------|-----|------|
| `PORT` | `8000` | API 포트 (기본값) |

---

## 🧪 테스트 방법

### 웹사이트 접속
```
https://myskin-web.onrender.com
```

### API 테스트
```bash
# 얼굴 분석
curl -X POST https://myskin-web.onrender.com/api/v1/analysis/face \
  -F "file=@test.jpg" \
  -F "user_id=test"

# 챗봇
curl -X POST https://myskin-web.onrender.com/api/v1/chatbot/chat \
  -F "message=피부 관리 방법 알려줘" \
  -F "user_id=test"

# GPU 서버 상태
curl https://myskin-web.onrender.com/api/v1/gpu/health
```

---

## 🔄 코드 수정 후 재배포

```bash
# 코드 수정 후
git add .
git commit -m "Update: 수정 내용"
git push origin main
```

**Render가 자동으로 감지하고 재배포합니다!** (3-5분 소요)

---

## ⚠️ 주의사항

### Render Free Tier 제한
- **15분 미사용 시 sleep 모드** (첫 요청 시 ~30초 대기)
- 월 750시간 무료 (충분함)
- PostgreSQL 1GB 저장공간

### GPU 서버 요구사항
- **PyTorch 모델**: GPU 메모리 2-4GB
- **LLaVA 챗봇**: GPU 메모리 **13GB 이상** (권장: RTX 3090/4090)
- **총 VRAM**: 최소 16GB (권장: 24GB)

### 보안 권장사항
1. GPU 서버에 API 키 인증 추가
2. 방화벽 설정으로 특정 IP만 허용
3. HTTPS 사용 (Let's Encrypt)

---

## 📊 GPU 서버 모니터링

```bash
# 로그 확인
tail -f inference.log

# GPU 사용량
watch -n 1 nvidia-smi

# 프로세스 확인
ps aux | grep inference_api
```

---

## 🎉 완료!

**최종 URL**: https://myskin-web.onrender.com

### 서비스 구성:
✅ 웹 프론트엔드 (Render)
✅ REST API (Render)
✅ PostgreSQL (Render)
✅ AI 이미지 분석 (GPU 서버)
✅ LLM 챗봇 (GPU 서버)

**총 비용: $0/월** 🎊

---

## 📚 참고 문서

- **무료 배포 상세 가이드**: `FREE_DEPLOYMENT.md`
- **GPU 서버 설정**: `gpu_server/README.md`
- **프로젝트 구조**: `CLAUDE.md`
- **Google Cloud 배포**: `DEPLOYMENT.md` (유료 옵션)
