"""
사용자 프로필 API 라우트
"""
from flask import Blueprint, request, jsonify
from services.history_service import ProfileService
from utils.decorators import handle_errors

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/api/v1/user/profile', methods=['POST'])
@handle_errors
def save_profile():
    """프로필 생성/수정"""
    data = request.get_json()
    result = ProfileService.save_profile(data)
    return jsonify(result)


@profile_bp.route('/api/v1/user/profile/<user_id>', methods=['GET'])
@handle_errors
def get_profile(user_id):
    """프로필 조회"""
    result = ProfileService.get_profile(user_id)
    return jsonify(result)
