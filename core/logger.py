"""
로깅 설정
"""
import logging
import sys
from pathlib import Path

def setup_logger(name='MySkinProject', level=logging.INFO):
    """
    애플리케이션 로거 설정

    Args:
        name: 로거 이름
        level: 로그 레벨

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 이미 핸들러가 있으면 추가하지 않음
    if logger.handlers:
        return logger

    # 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (선택적)
    try:
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / 'app.log', encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"파일 로깅 설정 실패: {e}")

    return logger
