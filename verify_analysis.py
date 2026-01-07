"""
AI 분석 결과 검증 스크립트
"""
from models import SessionLocal, AnalysisHistory
import json

def verify_latest_analysis():
    """최근 분석 결과를 상세히 출력"""
    db = SessionLocal()

    try:
        # 최근 분석 1개 조회
        latest = db.query(AnalysisHistory)\
            .order_by(AnalysisHistory.timestamp.desc())\
            .first()

        if not latest:
            print("❌ 분석 기록이 없습니다.")
            return

        print("\n" + "="*80)
        print("🔍 최근 AI 분석 결과 검증")
        print("="*80)

        print(f"\n📊 기본 정보:")
        print(f"   ID: {latest.id}")
        print(f"   사용자: {latest.user_id}")
        print(f"   분석 시각: {latest.timestamp}")
        print(f"   코스: {latest.course_name}")
        print(f"   종합 점수: {latest.overall_score}/100")

        print(f"\n🎯 부위별 분석 결과:")
        print("-"*80)

        regions = latest.regions
        for region_name, data in regions.items():
            print(f"\n   [{region_name.upper()}]")
            print(f"   점수: {data.get('score', 'N/A')}/100")
            print(f"   등급: {data.get('grade', 'N/A')}/10")
            print(f"   원본 등급: {data.get('raw_grade', 'N/A')}")

            # 상세 메트릭 (상위 5개만 표시)
            metrics = data.get('metrics', {})
            if metrics:
                print(f"   주요 지표:")
                sorted_metrics = sorted(metrics.items(), key=lambda x: x[1], reverse=True)
                for metric_name, value in sorted_metrics[:5]:
                    print(f"      • {metric_name}: {value:.1f}")

        print(f"\n💡 AI 추천:")
        print("-"*80)
        rec = latest.recommendation
        if rec:
            print(f"   LED 모드: {rec.get('mode', 'N/A').upper()}")
            print(f"   권장 시간: {rec.get('duration', 'N/A')}분")
            print(f"   강도: {rec.get('intensity', 'N/A')}%")
            print(f"   이유: {rec.get('reason', 'N/A')}")
            print(f"   BLE 명령: {rec.get('ble_command', 'N/A')}")

            print(f"\n   문제 분석:")
            issue_analysis = rec.get('issue_analysis', {})
            for issue, score in sorted(issue_analysis.items(), key=lambda x: x[1], reverse=True):
                print(f"      • {issue}: {score:.2f}")

        print(f"\n✅ 데이터 무결성 검증:")
        print("-"*80)

        # 검증 1: 모든 부위가 있는지
        expected_regions = ["forehead", "eye_l", "eye_r", "cheek_l", "cheek_r", "chin"]
        missing = [r for r in expected_regions if r not in regions]
        if missing:
            print(f"   ⚠️ 누락된 부위: {missing}")
        else:
            print(f"   ✓ 모든 부위 분석 완료 (6개)")

        # 검증 2: 점수 범위 체크
        invalid_scores = []
        for region_name, data in regions.items():
            score = data.get('score', 0)
            if not (0 <= score <= 100):
                invalid_scores.append(f"{region_name}: {score}")

        if invalid_scores:
            print(f"   ⚠️ 범위 벗어난 점수: {invalid_scores}")
        else:
            print(f"   ✓ 모든 점수가 0-100 범위 내")

        # 검증 3: 평균 점수 계산 확인
        avg_score = sum(data.get('score', 0) for data in regions.values()) / len(regions)
        if abs(avg_score - latest.overall_score) > 1:
            print(f"   ⚠️ 종합 점수 불일치: DB({latest.overall_score}) vs 계산({avg_score:.1f})")
        else:
            print(f"   ✓ 종합 점수 일치 (오차 < 1)")

        # 검증 4: 메트릭 개수 체크
        print(f"\n   부위별 메트릭 개수:")
        for region_name, data in regions.items():
            metrics_count = len(data.get('metrics', {}))
            print(f"      • {region_name}: {metrics_count}개")

        print("\n" + "="*80)
        print("🎉 검증 완료!")
        print("="*80 + "\n")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


def compare_analyses(user_id, limit=5):
    """사용자의 최근 분석들을 비교"""
    db = SessionLocal()

    try:
        records = db.query(AnalysisHistory)\
            .filter(AnalysisHistory.user_id == user_id)\
            .order_by(AnalysisHistory.timestamp.desc())\
            .limit(limit)\
            .all()

        if not records:
            print(f"❌ {user_id}의 분석 기록이 없습니다.")
            return

        print("\n" + "="*80)
        print(f"📈 {user_id}님의 분석 추이 비교 (최근 {len(records)}개)")
        print("="*80)

        print(f"\n{'날짜':<20} {'종합점수':<10} {'추천모드':<10} {'주요문제'}")
        print("-"*80)

        for record in records:
            date = record.timestamp.strftime('%Y-%m-%d %H:%M')
            score = record.overall_score
            mode = record.recommendation.get('mode', 'N/A').upper() if record.recommendation else 'N/A'

            # 주요 문제 찾기
            if record.recommendation and 'issue_analysis' in record.recommendation:
                issues = record.recommendation['issue_analysis']
                main_issue = max(issues, key=issues.get)
            else:
                main_issue = 'N/A'

            print(f"{date:<20} {score:<10} {mode:<10} {main_issue}")

        print("\n" + "="*80 + "\n")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == '__main__':
    print("\n🔍 MySkin AI 분석 결과 검증 도구\n")

    # 1. 최근 분석 상세 검증
    verify_latest_analysis()

    # 2. 사용자 ID 입력받아 추이 비교
    user_id = input("추이를 확인할 사용자 ID를 입력하세요 (Enter=건너뛰기): ").strip()
    if user_id:
        compare_analyses(user_id)
