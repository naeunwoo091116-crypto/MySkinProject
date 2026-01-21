FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# 시스템 패키지 및 gcloud SDK 설치 (gsutil 사용 위함)
RUN apt-get update && apt-get install -y curl python3-pip python3-dev && \
    curl https://sdk.cloud.google.com | bash
ENV PATH=/root/google-cloud-sdk/bin:$PATH

WORKDIR /app

# 1. PyTorch 설치 (CUDA 12.1 호환)
RUN pip3 install --no-cache-dir torch==2.1.0 --index-url https://download.pytorch.org/whl/cu121

# 2. 기본 라이브러리 설치
RUN pip3 install --no-cache-dir \
    transformers accelerate fastapi uvicorn Pillow \
    bitsandbytes tiktoken protobuf sentencepiece peft

# 3. SDPA는 PyTorch 2.0+에 기본 내장 (별도 설치 불필요)

# 2. 모델 파일 복사 (13GB - 모델이 안 변하면 구글이 이 단계를 캐싱함)
# 이 줄이 코드 복사보다 위에 있어야 합니다.
# [중요] 모델 폴더(final)는 복사하지 않습니다! (이미지 용량 대폭 감소)
COPY main.py .

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]