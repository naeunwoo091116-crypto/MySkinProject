"""
Render 무료 배포용 Flask 앱 (원격 GPU 서버 사용)
"""
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import io
from PIL import Image
import os

# Services - 원격 AI 서비스 사용
from services.analysis_service_remote import get_remote_analysis_service
from services.history_service import HistoryService, ProfileService
from services.led_service import LEDService
from services.remote_chatbot_service import get_remote_chatbot_service
from services.chat_history_service import ChatHistoryService
from models.database import init_db, get_db

# Blueprints
from routes.device import device_bp

app = Flask(__name__)

# Blueprint 등록
app.register_blueprint(device_bp)

# ==========================================
# 데이터베이스 설정 및 초기화
# ==========================================
try:
    init_db()
    print("[INFO] Database connection successful!")
except Exception as e:
    print(f"[WARNING] Database initialization error: {e}")

# ==========================================
# 싱글톤 서비스 인스턴스 (원격 AI 사용)
# ==========================================
analysis_service = get_remote_analysis_service()  # 원격 GPU 서버 사용
chatbot_service = None  # Lazy loading

# ==========================================
# 1. 서버 API - 메인 페이지
# ==========================================
@app.route('/')
def home():
    return render_template('index.html')

# ==========================================
# 2. 분석 API (원격 GPU 서버 사용)
# ==========================================
@app.route('/api/v1/analysis/face', methods=['POST'])
def analyze_face():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files['file']
    user_id = request.form.get('user_id', 'anonymous')

    try:
        # 1. 이미지 읽기
        image_bytes = file.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

        # 2. 원격 GPU 서버로 분석 (서비스 호출)
        result = analysis_service.analyze_face(pil_image, user_id)

        # 3. 타임스탬프 추가
        result['timestamp'] = datetime.now().isoformat()

        return jsonify(result)

    except ValueError as val_err:
        return jsonify({
            "error": "invalid_image",
            "message": str(val_err),
            "details": "얼굴이 포함된 사진을 업로드해주세요."
        }), 400

    except Exception as e:
        print(f"❌ 치명적 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ==========================================
# 3. 히스토리 관리 API
# ==========================================
@app.route('/api/v1/history', methods=['POST'])
def save_history():
    """분석 결과를 히스토리에 저장"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'anonymous')

        if 'overall_score' not in data or 'regions' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        result = HistoryService.save_analysis(user_id, data)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/history/<user_id>', methods=['GET'])
def get_history(user_id):
    """사용자별 히스토리 조회"""
    try:
        limit = request.args.get('limit', type=int, default=20)
        result = HistoryService.get_user_history(user_id, limit)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/stats/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """사용자 통계 조회"""
    try:
        result = HistoryService.get_user_stats(user_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# 4. 사용자 프로필 관리 API
# ==========================================
@app.route('/api/v1/user/profile', methods=['POST'])
def save_user_profile():
    """사용자 프로필 저장/수정"""
    try:
        data = request.get_json()
        result = ProfileService.save_profile(data)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/user/profile/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    """사용자 프로필 조회"""
    try:
        result = ProfileService.get_profile(user_id)
        if not result.get('success', True):
            return jsonify(result), 404
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/users', methods=['GET'])
def get_all_users():
    """모든 사용자 목록 조회"""
    try:
        users = ProfileService.get_all_users()
        return jsonify({"users": users})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """사용자 삭제"""
    try:
        result = ProfileService.delete_user(user_id)
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify(result), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# 6. 챗봇 상담 API
# ==========================================
@app.route('/api/v1/chatbot/chat', methods=['POST'])
def chat_with_bot():
    global chatbot_service
    try:
        if chatbot_service is None:
            chatbot_service = get_remote_chatbot_service()  # 원격 GPU 서버 사용

        user_id = request.form.get('user_id', 'anonymous')
        message = request.form.get('message', '')
        image_file = request.files.get('image')

        if not message and request.is_json:
            data = request.get_json()
            message = data.get('message', '')
            user_id = data.get('user_id', user_id)

        if not message and not image_file:
             return jsonify({"error": "No message or image provided"}), 400

        print(f"[Chatbot] User: {user_id}, Message: {message}, Image: {bool(image_file)}")

        reply = chatbot_service.generate_response(message, image_file)

        # 챗봇 대화 내용 저장
        try:
            from models.database import SessionLocal
            db = SessionLocal()
            ChatHistoryService.save_chat(db, user_id, message, reply)
            db.close()
        except Exception as save_err:
            print(f"Failed to save chat history: {save_err}")

        return jsonify({
            "reply": reply,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Chatbot Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/chatbot/history/<user_id>', methods=['GET'])
def get_chat_history(user_id):
    """챗봇 대화 내역 조회 API"""
    try:
        from models.database import SessionLocal
        db = SessionLocal()
        history = ChatHistoryService.get_history(db, user_id)
        db.close()
        return jsonify([h.to_dict() for h in history])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/user/login', methods=['POST'])
def login_user():
    """상세 로그인 검증 API"""
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')

    if not user_id:
        return jsonify({"success": False, "error": "User ID is required"}), 400

    result = ProfileService.verify_login(user_id, password)
    return jsonify(result)

# ==========================================
# GPU 서버 상태 확인
# ==========================================
@app.route('/api/v1/gpu/health', methods=['GET'])
def gpu_health():
    """GPU 서버 상태 확인"""
    try:
        from services.remote_ai_service import get_remote_ai_service
        remote_ai = get_remote_ai_service()
        health = remote_ai.health_check()
        return jsonify(health)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', debug=False, port=port)
