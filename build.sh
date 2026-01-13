#!/bin/bash
# Render 배포 시 자동 실행되는 빌드 스크립트

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Build complete!"
