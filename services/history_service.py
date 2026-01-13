"""
분석 히스토리 관리 서비스
"""
from datetime import datetime
from models.database import AnalysisHistory, User, ChatHistory, SessionLocal
from core.constants import MAX_HISTORY_ITEMS
from core.logger import setup_logger
from werkzeug.security import generate_password_hash, check_password_hash

logger = setup_logger(__name__)


class HistoryService:
    """히스토리 관리 서비스"""

    @staticmethod
    def save_analysis(user_id, analysis_data):
        """
        분석 결과 저장

        Args:
            user_id: 사용자 ID
            analysis_data: 분석 결과 데이터

        Returns:
            dict: 저장된 레코드 정보
        """
        db = SessionLocal()
        try:
            # 타임스탬프 처리
            timestamp_str = analysis_data.get('timestamp')
            if timestamp_str and isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.now()

            # 새 기록 생성
            new_record = AnalysisHistory(
                user_id=user_id,
                timestamp=timestamp,
                overall_score=analysis_data['overall_score'],
                regions=analysis_data['regions'],
                recommendation=analysis_data.get('recommendation', {}),
                course_name=analysis_data.get('course_name', 'AI 정밀 분석')
            )

            db.add(new_record)
            db.commit()
            db.refresh(new_record)

            logger.info(f"📝 히스토리 저장 완료: {user_id} - 점수 {analysis_data['overall_score']}")

            return {
                "success": True,
                "record_id": new_record.id,
                "message": "히스토리가 저장되었습니다."
            }

        except Exception as e:
            db.rollback()
            logger.error(f"❌ 히스토리 저장 오류: {e}")
            raise

        finally:
            db.close()

    @staticmethod
    def get_user_history(user_id, limit=MAX_HISTORY_ITEMS):
        """
        사용자 히스토리 조회

        Args:
            user_id: 사용자 ID
            limit: 최대 조회 개수

        Returns:
            dict: 히스토리 데이터
        """
        db = SessionLocal()
        try:
            # 데이터베이스에서 조회 (최신순)
            records = db.query(AnalysisHistory)\
                .filter(AnalysisHistory.user_id == user_id)\
                .order_by(AnalysisHistory.timestamp.desc())\
                .limit(limit)\
                .all()

            # 딕셔너리로 변환
            user_history = [record.to_dict() for record in records]

            return {
                "user_id": user_id,
                "total_records": len(user_history),
                "history": user_history
            }

        except Exception as e:
            logger.error(f"❌ 히스토리 조회 오류: {e}")
            raise

        finally:
            db.close()

    @staticmethod
    def get_user_stats(user_id):
        """
        사용자 통계 계산

        Args:
            user_id: 사용자 ID

        Returns:
            dict: 통계 데이터
        """
        db = SessionLocal()
        try:
            # 전체 히스토리 조회
            records = db.query(AnalysisHistory)\
                .filter(AnalysisHistory.user_id == user_id)\
                .order_by(AnalysisHistory.timestamp.desc())\
                .all()

            if not records:
                return {
                    "user_id": user_id,
                    "total_analyses": 0,
                    "average_score": 0,
                    "trend": "neutral",
                    "region_stats": {}
                }

            # 통계 계산
            scores = [r.overall_score for r in records]
            avg_score = sum(scores) / len(scores)

            # 추세 계산 (최근 5개 vs 전체)
            recent_scores = scores[:5]
            recent_avg = sum(recent_scores) / len(recent_scores)

            if recent_avg > avg_score + 5:
                trend = "improving"
            elif recent_avg < avg_score - 5:
                trend = "declining"
            else:
                trend = "stable"

            # 부위별 통계
            region_stats = {}
            for record in records:
                for region_name, region_data in record.regions.items():
                    if region_name not in region_stats:
                        region_stats[region_name] = []
                    region_stats[region_name].append(region_data.get('score', 0))

            region_averages = {
                region: round(sum(scores) / len(scores), 1)
                for region, scores in region_stats.items()
            }

            return {
                "user_id": user_id,
                "total_analyses": len(records),
                "average_score": round(avg_score, 1),
                "trend": trend,
                "region_stats": region_averages,
                "latest_score": scores[0] if scores else 0,
                "best_score": max(scores) if scores else 0,
                "worst_score": min(scores) if scores else 0
            }

        except Exception as e:
            logger.error(f"❌ 통계 계산 오류: {e}")
            raise

        finally:
            db.close()


class ProfileService:
    """사용자 프로필 관리 서비스"""

    @staticmethod
    def save_profile(profile_data):
        """
        프로필 저장/수정

        Args:
            profile_data: 프로필 데이터

        Returns:
            dict: 저장 결과
        """
        db = SessionLocal()
        try:
            user_id = profile_data.get('user_id')
            if not user_id:
                raise ValueError("user_id is required")

            # 기존 사용자 조회
            existing_user = db.query(User).filter(User.user_id == user_id).first()

            if existing_user:
                # 업데이트
                existing_user.name = profile_data.get('name', existing_user.name)
                existing_user.skin_type = profile_data.get('skin_type', existing_user.skin_type)
                existing_user.gender = profile_data.get('gender', existing_user.gender)
                existing_user.concerns = profile_data.get('concerns', existing_user.concerns)
                existing_user.goals = profile_data.get('goals', existing_user.goals)
                
                # 비밀번호가 제공된 경우에만 업데이트
                password = profile_data.get('password')
                if password:
                    existing_user.password_hash = generate_password_hash(password)
                
                existing_user.updated_at = datetime.now()

                db.commit()
                logger.info(f"📝 프로필 업데이트 완료: {user_id}")

                return {
                    "success": True,
                    "message": "프로필이 업데이트되었습니다.",
                    "profile": existing_user.to_dict()
                }

            else:
                # 새로 생성
                new_user = User(
                    user_id=user_id,
                    name=profile_data.get('name'),
                    skin_type=profile_data.get('skin_type'),
                    gender=profile_data.get('gender'),
                    concerns=profile_data.get('concerns', []),
                    goals=profile_data.get('goals', ''),
                    password_hash=generate_password_hash(profile_data.get('password', '1234')) # 기본값 1234
                )
 
                db.add(new_user)
                db.commit()
                db.refresh(new_user)

                logger.info(f"📝 새 프로필 생성 완료: {user_id}")

                return {
                    "success": True,
                    "message": "프로필이 생성되었습니다.",
                    "profile": new_user.to_dict()
                }

        except Exception as e:
            db.rollback()
            logger.error(f"❌ 프로필 저장 오류: {e}")
            raise

        finally:
            db.close()

    @staticmethod
    def get_profile(user_id):
        """
        프로필 조회

        Args:
            user_id: 사용자 ID

        Returns:
            dict: 프로필 데이터
        """
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()

            if user:
                return {
                    "success": True,
                    "profile": user.to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": "사용자를 찾을 수 없습니다."
                }

        except Exception as e:
            logger.error(f"❌ 프로필 조회 오류: {e}")
            raise

        finally:
            db.close()

    @staticmethod
    def verify_login(user_id, password):
        """
        사용자 로그인 검증
        """
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if user and user.password_hash:
                if check_password_hash(user.password_hash, password):
                    user.last_login_at = datetime.now()
                    db.commit()
                    return {"success": True, "profile": user.to_dict()}
            
            # 초기 버전 호환성: 비밀번호가 없는 경우 user_id만으로 로그인 허용 (선택 사항)
            if user and not user.password_hash:
                 user.last_login_at = datetime.now()
                 db.commit()
                 return {"success": True, "profile": user.to_dict()}

            return {"success": False, "error": "아이디 또는 비밀번호가 일치하지 않습니다."}
        except Exception as e:
            logger.error(f"❌ 로그인 검증 오류: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    @staticmethod
    def get_all_users():
        """
        모든 사용자 목록 조회

        Returns:
            list: 사용자 목록 ({user_id, name})
        """
        db = SessionLocal()
        try:
            users = db.query(User).all()
            return [
                {"user_id": u.user_id, "name": u.name, "created_at": u.created_at.isoformat()}
                for u in users
            ]
        except Exception as e:
            logger.error(f"❌ 사용자 목록 조회 오류: {e}")
            raise
        finally:
            db.close()

    @staticmethod
    def delete_user(user_id):
        """
        사용자 및 관련 데이터 삭제
        """
        db = SessionLocal()
        try:
            # 사용자 조회
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return {"success": False, "error": "사용자를 찾을 수 없습니다."}

            # 연관 데이터 삭제 (AnalysisHistory, ChatHistory)
            db.query(AnalysisHistory).filter(AnalysisHistory.user_id == user_id).delete()
            db.query(ChatHistory).filter(ChatHistory.user_id == user_id).delete()

            # 사용자 삭제
            db.delete(user)
            db.commit()
            
            logger.info(f"🗑️ 사용자 삭제 완료: {user_id}")
            return {"success": True, "message": "사용자가 삭제되었습니다."}
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 사용자 삭제 오류: {e}")
            raise
        finally:
            db.close()
