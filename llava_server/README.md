# LLaVA Server for MySkin Project

Vertex AI에 배포되는 LLaVA 기반 피부 상담 AI 서버입니다.

## 구조

```
llava_server/
├── main.py          # FastAPI 서버 (모델 로드 + 추론)
├── Dockerfile       # Docker 이미지 빌드 설정
└── README.md        # 이 파일
```

## 기술 스택

| 항목 | 사용 기술 |
|------|----------|
| Framework | FastAPI + Uvicorn |
| Model | LLaVA (llava-hf/llava-1.5-7b-hf 기반 Fine-tuned) |
| Inference | PyTorch 2.1 + SDPA (Scaled Dot Product Attention) |
| GPU | NVIDIA A100 (40GB) |
| Precision | FP16 (양자화 없음) |

## 모델 저장 위치

- **GCS 버킷**: `gs://skincare-model-storage/final`
- 서버 시작 시 자동으로 `/app/model_files`에 다운로드

## API 엔드포인트

### `GET /health`
헬스 체크

**Response:**
```json
{"status": "healthy"}
```

### `POST /predict`
피부 상담 요청

**Request:**
```json
{
  "instances": [
    {
      "prompt": "18세 남성이고 여드름이 고민입니다. 어떻게 관리해야 할까요?",
      "image": "base64_encoded_image (선택사항)"
    }
  ]
}
```

**Response:**
```json
{
  "predictions": [
    "Chain-of-Thought: 18세 남성의 경우..."
  ]
}
```

## 추론 설정

```python
model.generate(
    max_new_tokens=1024,      # 최대 토큰 수
    do_sample=False,          # Greedy decoding (환각 방지)
    repetition_penalty=1.1,   # 반복 방지
)
```

## 배포 방법

### 1. Docker 이미지 빌드 및 푸시

```bash
cd llava_server
gcloud builds submit --tag us-central1-docker.pkg.dev/skincare-data-platform/myskin-repo/llava-a100:latest . --timeout=2h
```

### 2. Vertex AI 모델 등록

```bash
gcloud ai models upload `
    --region=us-central1 `
    --display-name=llava-a100-optimized `
    --container-image-uri=us-central1-docker.pkg.dev/skincare-data-platform/myskin-repo/llava-a100:latest `
    --container-predict-route=/predict `
    --container-health-route=/health
```

### 3. 엔드포인트에 배포

```bash
gcloud ai endpoints deploy-model 2282954475658280960 `
    --region=us-central1 `
    --model=[모델_ID] `
    --display-name=llava-a100-deployment `
    --machine-type=a2-highgpu-1g `
    --accelerator="type=nvidia-tesla-a100,count=1" `
    --traffic-split=0=100 `
    --service-account="203772565653-compute@developer.gserviceaccount.com"
```

## 최적화 사항

### 속도 최적화
- **FP16**: 양자화 없이 FP16으로 로드 (A100 VRAM 충분)
- **SDPA**: PyTorch 2.0 내장 Scaled Dot Product Attention 사용
- **Greedy Decoding**: `do_sample=False`로 환각 방지 + 속도 향상

### 후처리
- `\n\n` 이후 반복되는 내용 자동 제거
- Chain-of-Thought + Answer 구조 유지

## 환경 변수

| 변수 | 설명 |
|------|------|
| `PYTHONUNBUFFERED` | 1 (로그 버퍼링 비활성화) |

## 트러블슈팅

### 타임아웃 (503/504)
- 원인: 모델 추론 시간 > 60초
- 해결: `max_new_tokens` 줄이기 또는 GPU 업그레이드

### 환각 (이상한 단어 생성)
- 원인: `do_sample=True` + 높은 `repetition_penalty`
- 해결: `do_sample=False` 사용 (Greedy decoding)

### 답변 반복
- 원인: 모델이 같은 내용을 다시 생성
- 해결: 후처리에서 `\n\n` 이후 중복 제거

## 버전 히스토리

| 버전 | 변경 사항 |
|------|----------|
| v1 | 초기 배포 (4-bit 양자화) |
| v2 | FP16 전환 + SDPA 추가 |
| v3 | Greedy decoding으로 환각 방지 |
| v4 | 후처리 로직 개선 |
