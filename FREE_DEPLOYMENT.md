# 🚀 무료 배포 가이드 (GitHub 연동)

프로젝트 폴더를 GitHub에 업로드하고 자동으로 무료 배포하는 가이드입니다.

---

## 📋 배포 구조

```
┌─────────────────┐      API 호출       ┌──────────────────┐
│  Render (무료)   │  ────────────────> │  GPU 서버 (별도)  │
│  - Flask 웹앱    │  <────────────────  │  - AI 추론 API   │
│  - PostgreSQL DB │      결과 반환       │  - PyTorch 모델  │
│  - 프론트엔드     │                     │  - CUDA          │
└─────────────────┘                     └──────────────────┘
```

**비용**: 완전 무료 (Render Free Tier)
**배포 시간**: 10-15분
**URL**: `https://myskin-web.onrender.com`

---

## 🎯 Step 1: GitHub에 코드 업로드

### 1-1. Git 초기화 (처음만)

```bash
cd C:\Users\user\Downloads\MySkinProject
git init
```

### 1-2. 파일 추가 및 커밋

```bash
# 모든 파일 추가 (.gitignore에 명시된 파일 제외)
git add .

# 커밋
git commit -m "Initial commit - MySkin project"
```

### 1-3. GitHub 리포지토리 생성

1. https://github.com 접속 후 로그인
2. 우측 상단 `+` > `New repository` 클릭
3. 설정:
   - Repository name: `MySkinProject`
   - Public 또는 Private 선택
   - **체크박스는 모두 비활성화** (README, .gitignore, license 추가 안 함)
4. `Create repository` 클릭

### 1-4. GitHub에 푸시

```bash
# GitHub 리포지토리 연결 (YOUR_USERNAME을 본인 GitHub 아이디로 변경)
git remote add origin https://github.com/YOUR_USERNAME/MySkinProject.git

# main 브랜치로 푸시
git branch -M main
git push -u origin main
```

**완료!** 이제 GitHub에서 코드를 확인할 수 있습니다.

---

## 🌐 Step 2: Render에 배포

### 2-1. Render 계정 생성

1. https://render.com 접속
2. `Get Started` > `Sign up with GitHub` 클릭
3. GitHub 계정으로 로그인 (연동 승인)

### 2-2. PostgreSQL 데이터베이스 생성

1. Render 대시보드 > `New` > `PostgreSQL` 클릭
2. 설정:
   - **Name**: `myskin-db`
   - **Database**: `myskin`
   - **User**: `postgres` (자동 생성)
   - **Region**: `Singapore (Southeast Asia)` (한국과 가장 가까움)
   - **Plan**: **Free** 선택
3. `Create Database` 클릭
4. 생성 완료 후 **Internal Database URL** 복사 (나중에 사용)

### 2-3. Web Service 생성

1. Render 대시보드 > `New` > `Web Service` 클릭
2. `Connect a repository` > GitHub 리포지토리 선택
   - 리포지토리가 안 보이면 `Configure account` 클릭 후 권한 부여
3. 설정:
   - **Name**: `myskin-web`
   - **Region**: `Singapore`
   - **Branch**: `main`
   - **Root Directory**: (비워둠)
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn -b 0.0.0.0:$PORT app:app --workers 2 --timeout 120`
   - **Plan**: **Free** 선택

### 2-4. 환경 변수 설정

**Environment Variables** 섹션에서 `Add Environment Variable` 클릭:

| Key | Value | 설명 |
|-----|-------|------|
| `PYTHON_VERSION` | `3.11.0` | Python 버전 |
| `DATABASE_URL` | (2-2에서 복사한 URL) | PostgreSQL 연결 |
| `GPU_SERVER_URL` | `http://YOUR_GPU_SERVER_IP:8000` | GPU 서버 주소 (나중에 설정 가능) |

4. `Create Web Service` 클릭

### 2-5. 배포 대기

- 첫 배포는 10-15분 소요
- 로그에서 진행 상황 확인 가능
- **배포 완료 시 URL 생성**: `https://myskin-web.onrender.com`

---

## 🖥️ Step 3: GPU 서버 설정 (별도 서버)

GPU 서버가 따로 있다면 AI 추론 API를 배포합니다.

### 3-1. GPU 서버에 파일 업로드

**필요한 파일/폴더:**
```
MySkinProject/
├── gpu_server/
│   ├── inference_api.py
│   └── requirements.txt
├── models/
│   ├── *.pth (모든 모델 파일)
│   └── ai_models.py
├── services/
│   ├── ai_service.py
│   └── image_service.py
└── core/
    ├── config.py
    ├── constants.py
    └── logger.py
```

**업로드 방법:**
```bash
# 예: SCP로 업로드
scp -r MySkinProject username@gpu-server-ip:/home/username/
```

### 3-2. GPU 서버에서 실행

```bash
# GPU 서버 SSH 접속
ssh username@gpu-server-ip

# 프로젝트 디렉토리로 이동
cd MySkinProject/gpu_server

# 의존성 설치
pip install -r requirements.txt

# API 서버 실행 (백그라운드)
nohup python inference_api.py > inference.log 2>&1 &

# 서버 확인
curl http://localhost:8000/
```

### 3-3. 방화벽 포트 열기

```bash
# Ubuntu/Debian
sudo ufw allow 8000

# 서버 공인 IP 확인
curl ifconfig.me
```

### 3-4. Render에 GPU 서버 URL 등록

1. Render 대시보드 > `myskin-web` 서비스 클릭
2. `Environment` 탭 > `Add Environment Variable`
3. 추가:
   - **Key**: `GPU_SERVER_URL`
   - **Value**: `http://YOUR_GPU_SERVER_IP:8000`
4. `Save Changes` 클릭 (자동 재배포됨)

---

## ✅ Step 4: 배포 테스트

### 4-1. 웹사이트 접속

브라우저에서 Render URL 접속:
```
https://myskin-web.onrender.com
```

### 4-2. API 테스트

```bash
# 얼굴 분석 API
curl -X POST https://myskin-web.onrender.com/api/v1/analysis/face \
  -F "file=@test_image.jpg" \
  -F "user_id=test_user"

# GPU 서버 상태 확인
curl https://myskin-web.onrender.com/api/v1/gpu/health
```

### 4-3. 데이터베이스 확인

Render 대시보드 > `myskin-db` > `Connect` 탭에서 psql 명령어 복사:
```bash
psql postgres://user:password@host/myskin

# 테이블 확인
\dt
```

---

## 🔄 코드 수정 후 재배포

### 자동 배포 (GitHub 연동)

```bash
# 코드 수정 후
git add .
git commit -m "Update: 수정 내용"
git push origin main
```

**자동으로 Render가 감지하고 재배포합니다!** (약 3-5분 소요)

### 수동 배포

Render 대시보드 > `myskin-web` > `Manual Deploy` > `Deploy latest commit`

---

## 🛠️ 문제 해결

### 1. 배포 실패 시

**로그 확인:**
- Render 대시보드 > `myskin-web` > `Logs` 탭

**흔한 오류:**
- `requirements.txt not found`: `build.sh` 파일 확인
- `Module not found`: requirements.txt에 패키지 추가 누락
- `Database connection failed`: `DATABASE_URL` 환경 변수 확인

### 2. 무료 티어 제한

**Render Free 제한:**
- 15분 미사용 시 서비스 **sleep 모드** (첫 요청 시 ~30초 대기)
- 월 750시간 무료 (충분함)
- PostgreSQL 1GB 저장 공간

**해결책:**
- 주기적 핑 보내기 (UptimeRobot 등 사용)
- 유료 플랜 업그레이드 ($7/월)

### 3. GPU 서버 연결 실패

```bash
# GPU 서버에서 로그 확인
tail -f inference.log

# 포트 확인
netstat -tuln | grep 8000

# 방화벽 확인
sudo ufw status
```

---

## 💰 비용 정리

| 서비스 | 플랜 | 비용 |
|--------|------|------|
| Render Web Service | Free | $0 |
| Render PostgreSQL | Free (1GB) | $0 |
| **총 비용** | | **$0/월** |

**GPU 서버**: 별도 운영 (본인 서버)

---

## 📊 모니터링

### Render 대시보드

- **Metrics**: CPU, 메모리, 요청 수 확인
- **Logs**: 실시간 로그 스트리밍
- **Events**: 배포 히스토리

### GPU 서버 모니터링

```bash
# 로그 확인
tail -f inference.log

# GPU 사용량
watch -n 1 nvidia-smi

# 프로세스 확인
ps aux | grep inference_api
```

---

## 🎉 배포 완료!

**최종 URL:**
- 웹사이트: `https://myskin-web.onrender.com`
- API 엔드포인트: `https://myskin-web.onrender.com/api/v1/...`

**다음 단계:**
1. 커스텀 도메인 연결 (선택사항)
2. HTTPS 인증서 (Render가 자동 제공)
3. 모니터링 설정

---

## 📞 참고 자료

- [Render 문서](https://render.com/docs)
- [GitHub 가이드](https://docs.github.com/en/get-started)
- [Flask 배포 가이드](https://flask.palletsprojects.com/en/latest/deploying/)

---

## 🔐 보안 권장사항

### 환경 변수로 비밀 정보 관리

Render의 Environment Variables에 저장:
- `DATABASE_URL`
- `GPU_API_KEY` (GPU 서버 API 키)
- `SECRET_KEY` (Flask secret key)

### CORS 설정

특정 도메인만 허용하도록 수정 권장

### API 속도 제한

무료 티어 남용 방지를 위해 Flask-Limiter 사용 권장

---

배포 중 문제가 발생하면 Render 로그를 확인하세요!
