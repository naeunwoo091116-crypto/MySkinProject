# GPU 서버 배포 가이드

이 디렉토리는 GPU 서버에서 AI 모델 추론만 담당하는 독립적인 API입니다.

## 설치 및 실행

### 1. GPU 서버에 파일 업로드

다음 파일들을 GPU 서버로 복사:
```
gpu_server/
├── inference_api.py
├── requirements.txt
└── README.md

models/
├── forehead_model.pth
├── left_eye_model.pth
├── right_eye_model.pth
├── left_cheek_model.pth
├── right_cheek_model.pth
├── chin_model.pth
└── ai_models.py

services/
├── ai_service.py
└── image_service.py

core/
├── config.py
├── constants.py
└── logger.py
```

### 2. 의존성 설치

```bash
cd gpu_server
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
# 기본 포트 8000
python inference_api.py

# 커스텀 포트
PORT=5000 python inference_api.py

# 백그라운드 실행 (Linux)
nohup python inference_api.py > inference.log 2>&1 &
```

### 4. 외부 접근 설정

**방화벽 포트 열기:**
```bash
# Ubuntu/Debian
sudo ufw allow 8000

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

**공인 IP 확인:**
```bash
curl ifconfig.me
```

### 5. API 테스트

```bash
# Health check
curl http://YOUR_GPU_SERVER_IP:8000/

# 추론 테스트
curl -X POST http://YOUR_GPU_SERVER_IP:8000/api/v1/inference \
  -F "file=@test_image.jpg"

# 챗봇 테스트
curl -X POST http://YOUR_GPU_SERVER_IP:8000/api/v1/chatbot \
  -F "message=안녕하세요"
```

## API 엔드포인트

### GET /
Health check 및 GPU 상태 확인

**Response:**
```json
{
  "status": "ok",
  "service": "MySkin AI Inference API",
  "gpu_available": true,
  "device": "cuda:0"
}
```

### POST /api/v1/inference
얼굴 이미지 분석 (PyTorch ResNet)

**Input (multipart/form-data):**
- `file`: 이미지 파일

**Response:**
```json
{
  "success": true,
  "predictions": {
    "forehead": { "score": 75, "metrics": {...} },
    "eye_l": { "score": 80, "metrics": {...} },
    ...
  },
  "device": "cuda:0"
}
```

### POST /api/v1/chatbot
LLM 챗봇 응답 생성 (LLaVA 1.5 7B)

**Input (multipart/form-data):**
- `message`: 사용자 메시지 (필수)
- `image`: 이미지 파일 (선택사항)

**Response:**
```json
{
  "success": true,
  "reply": "피부 관리에 대한 답변...",
  "device": "cuda"
}
```

**⚠️ 중요:**
- 첫 요청 시 LLaVA 7B 모델 로딩으로 **1-2분** 소요
- 모델 크기: **약 13GB** (VRAM 요구사항)
- 권장 GPU: RTX 3090/4090 이상 (24GB VRAM)

### GET /api/v1/health
서버 상태 확인

**Response:**
```json
{
  "status": "healthy",
  "gpu_available": true,
  "device": "cuda:0",
  "models_loaded": true,
  "chatbot_loaded": false
}
```
- `chatbot_loaded`: LLM 모델 로드 여부 (첫 요청 전에는 false)

## 보안 설정 (권장)

### API 키 인증 추가

`inference_api.py`에 다음 추가:

```python
from functools import wraps

API_KEY = "your-secret-api-key-here"

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/v1/inference', methods=['POST'])
@require_api_key
def inference():
    ...
```

### HTTPS 설정 (권장)

```bash
# Let's Encrypt 무료 SSL 인증서
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com
```

gunicorn으로 실행:
```bash
pip install gunicorn
gunicorn -b 0.0.0.0:8000 inference_api:app --workers 2
```

## 모니터링

### 로그 확인
```bash
tail -f inference.log
```

### GPU 사용량 모니터링
```bash
watch -n 1 nvidia-smi
```

## 트러블슈팅

### CUDA out of memory
- `ai_service.py`에서 배치 크기 줄이기
- 또는 CPU 모드로 폴백

### 포트 이미 사용 중
```bash
# 포트 사용 프로세스 확인
lsof -i :8000
# 또는
netstat -tuln | grep 8000

# 프로세스 종료
kill -9 <PID>
```

### 방화벽 차단
- 클라우드 보안 그룹 확인 (AWS, GCP, Azure)
- 로컬 방화벽 규칙 확인

## 성능 최적화

### Gunicorn으로 멀티 워커 실행
```bash
gunicorn -b 0.0.0.0:8000 inference_api:app \
  --workers 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### systemd 서비스 등록 (자동 시작)

`/etc/systemd/system/myskin-inference.service`:
```ini
[Unit]
Description=MySkin AI Inference API
After=network.target

[Service]
User=your-username
WorkingDirectory=/path/to/gpu_server
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python inference_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

활성화:
```bash
sudo systemctl enable myskin-inference
sudo systemctl start myskin-inference
sudo systemctl status myskin-inference
```
