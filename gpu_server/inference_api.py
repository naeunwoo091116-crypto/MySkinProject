"""
GPU 서버용 AI 추론 API
이 파일을 GPU 서버에 배포하여 AI 모델 추론만 담당합니다.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import io
from PIL import Image
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_service import AIService
from services.image_service import ImageService
from services.chatbot_service import get_chatbot_service
from core.logger import setup_logger

app = Flask(__name__)
CORS(app)  # 모든 도메인에서 API 호출 허용

logger = setup_logger(__name__)

# AI 서비스 초기화 (GPU 사용)
ai_service = AIService()
image_service = ImageService()

# 챗봇 서비스 (Lazy loading - 첫 요청 시 로드)
chatbot_service = None

@app.route('/')
def home():
    """Health check"""
    return jsonify({
        "status": "ok",
        "service": "MySkin AI Inference API",
        "gpu_available": torch.cuda.is_available(),
        "device": str(ai_service.device)
    })

@app.route('/api/v1/inference', methods=['POST'])
def inference():
    """
    AI 모델 추론 API

    Input (multipart/form-data):
        - file: 얼굴 이미지

    Output:
        - regions: 부위별 분석 결과
        - overall_score: 전체 점수
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']

        # 1. 이미지 읽기
        image_bytes = file.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

        # 2. 이미지 검증 (얼굴 감지)
        is_valid, message = image_service.validate_image(pil_image)
        if not is_valid:
            return jsonify({
                "error": "invalid_image",
                "message": message
            }), 400

        # 3. AI 모델 추론 (GPU에서 실행)
        predictions = ai_service.predict_all_regions(pil_image)

        logger.info(f"✅ Inference completed on {ai_service.device}")

        return jsonify({
            "success": True,
            "predictions": predictions,
            "device": str(ai_service.device)
        })

    except ValueError as val_err:
        logger.error(f"Validation error: {val_err}")
        return jsonify({
            "error": "invalid_image",
            "message": str(val_err)
        }), 400

    except Exception as e:
        logger.error(f"Inference error: {e}", exc_info=True)
        return jsonify({
            "error": "inference_failed",
            "message": str(e)
        }), 500

@app.route('/api/v1/chatbot', methods=['POST'])
def chatbot():
    """
    LLM 챗봇 API (GPU에서 실행)

    Input (multipart/form-data):
        - message: 사용자 메시지
        - image: 이미지 파일 (선택사항)

    Output:
        - reply: 챗봇 응답
    """
    global chatbot_service

    try:
        # Lazy loading - 첫 요청 시 모델 로드
        if chatbot_service is None:
            logger.info("🤖 Loading chatbot model (first request)...")
            chatbot_service = get_chatbot_service()

        # 메시지 가져오기
        message = request.form.get('message', '')
        image_file = request.files.get('image')

        # JSON 요청 처리
        if not message and request.is_json:
            data = request.get_json()
            message = data.get('message', '')

        if not message and not image_file:
            return jsonify({"error": "No message or image provided"}), 400

        logger.info(f"💬 Chatbot request: {message[:50]}...")

        # 챗봇 응답 생성 (GPU에서 실행)
        reply = chatbot_service.generate_response(message, image_file)

        logger.info(f"✅ Chatbot response generated")

        return jsonify({
            "success": True,
            "reply": reply,
            "device": "cuda" if torch.cuda.is_available() else "cpu"
        })

    except Exception as e:
        logger.error(f"Chatbot error: {e}", exc_info=True)
        return jsonify({
            "error": "chatbot_failed",
            "message": str(e)
        }), 500

@app.route('/api/v1/health', methods=['GET'])
def health():
    """서버 상태 체크"""
    return jsonify({
        "status": "healthy",
        "gpu_available": torch.cuda.is_available(),
        "device": str(ai_service.device),
        "models_loaded": ai_service.models is not None,
        "chatbot_loaded": chatbot_service is not None
    })

if __name__ == '__main__':
    # GPU 서버에서 실행
    # 외부 접근을 위해 0.0.0.0으로 바인딩
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
