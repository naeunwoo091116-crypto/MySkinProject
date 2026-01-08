from flask import Flask, render_template, request, jsonify
from datetime import datetime
import io
from PIL import Image

# Services
from services.analysis_service import get_analysis_service
from services.history_service import HistoryService, ProfileService
from services.led_service import LEDService
from models.database import init_db

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
    print("✅ 데이터베이스 연결 성공!")
except Exception as e:
    print(f"⚠️ 데이터베이스 초기화 오류: {e}")
    # 필요한 경우 여기에 대체 로직 추가

# ==========================================
# 싱글톤 서비스 인스턴스 가져오기
# ==========================================
analysis_service = get_analysis_service()

# ==========================================
# 1. 서버 API - 메인 페이지
# ==========================================
@app.route('/')
def home():
    return render_template('index.html')

# ==========================================
# 2. 분석 API
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

        # 2. 서비스 호출 (유효성 검사, AI 분석, LED 추천 포함)
        result = analysis_service.analyze_face(pil_image, user_id)

        # 3. 타임스탬프 추가 (프론트엔드 호환성)
        result['timestamp'] = datetime.now().isoformat()

        return jsonify(result)

    except ValueError as val_err:
        # 이미지 유효성 검사 실패 등 (invalid_image)
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
# 5. BLE 디바이스 설정 API
# ==========================================
# device_bp (Blueprint)로 이동됨

if __name__ == '__main__':
    # 0.0.0.0으로 설정하여 모든 네트워크 인터페이스에서 접근 가능
    # 모바일 앱에서 연결하려면 필수!
    app.run(host='0.0.0.0', debug=True, port=5001)

