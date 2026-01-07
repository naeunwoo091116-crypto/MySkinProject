"""
API 데코레이터
"""
from functools import wraps
from flask import jsonify
from core.logger import setup_logger

logger = setup_logger(__name__)


def handle_errors(f):
    """API 에러 핸들링 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"입력 오류: {e}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"API 오류: {e}", exc_info=True)
            return jsonify({"error": "서버 오류가 발생했습니다"}), 500
    return decorated_function
