"""
통계 API 라우트
"""
from flask import Blueprint, jsonify
from services.history_service import HistoryService
from utils.decorators import handle_errors

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/api/v1/stats/<user_id>', methods=['GET'])
@handle_errors
def get_stats(user_id):
    """사용자 통계 조회"""
    result = HistoryService.get_user_stats(user_id)
    return jsonify(result)
