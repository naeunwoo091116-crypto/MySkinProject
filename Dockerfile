FROM python:3.10-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir "protobuf==3.20.3" "numpy<2.0.0"
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

# 타임아웃 300초 설정
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "8", "--timeout", "300", "app:app"]