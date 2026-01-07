"""
히스토리 API 라우트
"""
from flask import Blueprint, request, jsonify
from services.history_service import HistoryService
from utils.decorators import handle_errors

history_bp = Blueprint('history', __name__)


@history_bp.route('/api/v1/history', methods=['POST'])
@handle_errors
def save_history():
    """분석 결과 저장"""
    data = request.get_json()
    user_id = data.get('user_id', 'anonymous')

    # 필수 필드 확인
    if 'overall_score' not in data or 'regions' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    result = HistoryService.save_analysis(user_id, data)
    return jsonify(result)


@history_bp.route('/api/v1/history/<user_id>', methods=['GET'])
@handle_errors
def get_history(user_id):
    """사용자 히스토리 조회"""
    limit = request.args.get('limit', type=int, default=20)
    result = HistoryService.get_user_history(user_id, limit)
    return jsonify(result)
