"""
피부 분석 API 라우트
"""
from flask import Blueprint, request, jsonify
from PIL import Image
import io
from services.analysis_service import get_analysis_service
from utils.decorators import handle_errors
from core.logger import setup_logger

logger = setup_logger(__name__)

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/api/v1/analysis/face', methods=['POST'])
@handle_errors
def analyze_face():
    """피부 분석 API"""
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files['file']
    user_id = request.form.get('user_id', 'anonymous')

    # 이미지 읽기
    image_bytes = file.read()
    pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

    # 분석 수행
    analysis_service = get_analysis_service()
    result = analysis_service.analyze_face(pil_image, user_id)

    return jsonify(result)
