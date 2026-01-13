from sqlalchemy.orm import Session
from models.database import ChatHistory
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ChatHistoryService:
    @staticmethod
    def save_chat(db: Session, user_id: str, message: str, reply: str, image_path: str = None):
        """상담 내역 저장"""
        try:
            chat = ChatHistory(
                user_id=user_id,
                message=message,
                reply=reply,
                image_path=image_path,
                timestamp=datetime.utcnow()
            )
            db.add(chat)
            db.commit()
            db.refresh(chat)
            return chat
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving chat history: {e}")
            return None

    @staticmethod
    def get_history(db: Session, user_id: str, limit: int = 50):
        """사용자별 상담 내역 조회"""
        try:
            return db.query(ChatHistory)\
                .filter(ChatHistory.user_id == user_id)\
                .order_by(ChatHistory.timestamp.asc())\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error retrieving chat history: {e}")
            return []
