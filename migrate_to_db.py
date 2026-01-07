"""
JSON 파일에서 PostgreSQL로 데이터 마이그레이션 스크립트

사용법:
    python migrate_to_db.py

주의:
    - PostgreSQL이 실행 중이어야 합니다
    - .env 파일에 DATABASE_URL이 설정되어 있어야 합니다
    - data/history.json과 data/users.json 파일이 있어야 합니다
"""

import json
from pathlib import Path
from datetime import datetime
from models import SessionLocal, User, AnalysisHistory, init_db

# JSON 파일 경로
DATA_DIR = Path(__file__).parent / "data"
HISTORY_FILE = DATA_DIR / "history.json"
USERS_FILE = DATA_DIR / "users.json"


def load_json(filepath):
    """JSON 파일 로드"""
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return [] if filepath == HISTORY_FILE else {}


def migrate_users():
    """사용자 데이터 마이그레이션"""
    print("\n" + "="*50)
    print("👤 사용자 프로필 마이그레이션 시작")
    print("="*50)

    users_data = load_json(USERS_FILE)

    if not users_data:
        print("⚠️ users.json 파일이 비어있거나 없습니다.")
        return 0

    db = SessionLocal()
    migrated_count = 0

    try:
        for user_id, profile in users_data.items():
            # 기존 사용자 확인
            existing = db.query(User).filter(User.user_id == user_id).first()

            if existing:
                print(f"⏭️ 건너뛰기: {user_id} (이미 존재)")
                continue

            # 새 사용자 생성
            new_user = User(
                user_id=user_id,
                name=profile.get('name', ''),
                skin_type=profile.get('skin_type', ''),
                concerns=profile.get('concerns', []),
                goals=profile.get('goals', ''),
                created_at=datetime.fromisoformat(profile['created_at']) if profile.get('created_at') else datetime.now(),
                updated_at=datetime.fromisoformat(profile['updated_at']) if profile.get('updated_at') else datetime.now()
            )

            db.add(new_user)
            migrated_count += 1
            print(f"✅ 추가됨: {user_id} - {profile.get('name', 'N/A')}")

        db.commit()
        print(f"\n✅ 사용자 마이그레이션 완료: {migrated_count}명")

    except Exception as e:
        db.rollback()
        print(f"❌ 사용자 마이그레이션 오류: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

    return migrated_count


def migrate_history():
    """히스토리 데이터 마이그레이션"""
    print("\n" + "="*50)
    print("📝 분석 히스토리 마이그레이션 시작")
    print("="*50)

    history_data = load_json(HISTORY_FILE)

    if not history_data:
        print("⚠️ history.json 파일이 비어있거나 없습니다.")
        return 0

    db = SessionLocal()
    migrated_count = 0
    skipped_count = 0

    try:
        for record in history_data:
            # 기존 기록 확인 (user_id + timestamp로 중복 체크)
            timestamp_str = record.get('timestamp')
            if not timestamp_str:
                print(f"⏭️ 건너뛰기: timestamp 없음")
                skipped_count += 1
                continue

            # ISO 형식 timestamp 파싱
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()

            user_id = record.get('user_id', 'anonymous')

            # 중복 확인
            existing = db.query(AnalysisHistory).filter(
                AnalysisHistory.user_id == user_id,
                AnalysisHistory.timestamp == timestamp
            ).first()

            if existing:
                print(f"⏭️ 건너뛰기: {user_id} - {timestamp_str} (이미 존재)")
                skipped_count += 1
                continue

            # 새 기록 생성
            new_record = AnalysisHistory(
                user_id=user_id,
                timestamp=timestamp,
                overall_score=record.get('overall_score', 0),
                regions=record.get('regions', {}),
                recommendation=record.get('recommendation', {}),
                course_name=record.get('course_name', 'AI 정밀 분석')
            )

            db.add(new_record)
            migrated_count += 1
            print(f"✅ 추가됨: {user_id} - 점수 {record.get('overall_score')} - {timestamp_str[:10]}")

        db.commit()
        print(f"\n✅ 히스토리 마이그레이션 완료: {migrated_count}개 추가, {skipped_count}개 건너뜀")

    except Exception as e:
        db.rollback()
        print(f"❌ 히스토리 마이그레이션 오류: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

    return migrated_count


def verify_migration():
    """마이그레이션 검증"""
    print("\n" + "="*50)
    print("🔍 마이그레이션 검증")
    print("="*50)

    db = SessionLocal()

    try:
        user_count = db.query(User).count()
        history_count = db.query(AnalysisHistory).count()

        print(f"📊 데이터베이스 현황:")
        print(f"   - 사용자: {user_count}명")
        print(f"   - 분석 기록: {history_count}개")

        # 최근 기록 5개 샘플 출력
        recent_records = db.query(AnalysisHistory)\
            .order_by(AnalysisHistory.timestamp.desc())\
            .limit(5)\
            .all()

        if recent_records:
            print(f"\n📋 최근 기록 샘플 ({len(recent_records)}개):")
            for i, record in enumerate(recent_records, 1):
                print(f"   {i}. {record.user_id} - 점수 {record.overall_score} - {record.timestamp}")

    except Exception as e:
        print(f"❌ 검증 오류: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


def main():
    """메인 마이그레이션 실행"""
    print("\n" + "="*60)
    print("🚀 MySkin 프로젝트 데이터 마이그레이션")
    print("   JSON → PostgreSQL")
    print("="*60)

    # 1. 데이터베이스 테이블 생성
    print("\n1️⃣ 데이터베이스 테이블 생성 중...")
    try:
        init_db()
        print("✅ 테이블 생성 완료!")
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        print("\n⚠️ PostgreSQL이 실행 중인지 확인하세요.")
        print("   Docker: docker ps | grep postgres")
        print("   로컬: 서비스가 실행 중인지 확인")
        return

    # 2. 사용자 마이그레이션
    user_count = migrate_users()

    # 3. 히스토리 마이그레이션
    history_count = migrate_history()

    # 4. 검증
    verify_migration()

    # 5. 요약
    print("\n" + "="*60)
    print("✅ 마이그레이션 완료!")
    print(f"   - 사용자: {user_count}명 마이그레이션")
    print(f"   - 히스토리: {history_count}개 마이그레이션")
    print("="*60)

    if user_count > 0 or history_count > 0:
        print("\n💡 다음 단계:")
        print("   1. 데이터 확인: psql -U postgres -d myskin")
        print("   2. Flask 서버 실행: python app.py")
        print("   3. 기존 JSON 파일 백업 (선택사항)")
    else:
        print("\n⚠️ 마이그레이션된 데이터가 없습니다.")
        print("   JSON 파일을 확인하세요:")
        print(f"   - {HISTORY_FILE}")
        print(f"   - {USERS_FILE}")


if __name__ == '__main__':
    main()
