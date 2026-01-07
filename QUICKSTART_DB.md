# PostgreSQL 연동 빠른 시작 가이드

## ⚡ 3분 안에 시작하기

### 1단계: PostgreSQL 설치 (Docker 추천)

```bash
# Docker로 PostgreSQL 실행 (가장 간단)
docker run --name myskin-postgres -e POSTGRES_PASSWORD=myskin123 -e POSTGRES_DB=myskin -p 5432:5432 -d postgres:15
```

**Docker가 없다면?**
- Windows: https://www.postgresql.org/download/windows/
- 설치 시 비밀번호: `myskin123`, 포트: `5432`
- 설치 후 데이터베이스 생성: `CREATE DATABASE myskin;`

---

### 2단계: 데이터베이스 테이블 생성

```bash
# 프로젝트 폴더에서 실행
python models.py
```

**성공 메시지:**
```
✅ Database tables created successfully!
```

---

### 3단계: 기존 데이터 마이그레이션 (선택사항)

JSON 파일에 데이터가 있다면:

```bash
python migrate_to_db.py
```

---

### 4단계: 서버 실행

```bash
python app.py
```

**정상 실행 시:**
```
✅ 데이터베이스 연결 성공!
 * Running on http://localhost:5000
```

---

## ✅ 완료!

이제 애플리케이션이 PostgreSQL을 사용합니다.

### 데이터 확인

```bash
# Docker 사용 시
docker exec -it myskin-postgres psql -U postgres -d myskin

# PostgreSQL 명령어
\dt                          # 테이블 목록
SELECT COUNT(*) FROM users;  # 사용자 수
SELECT COUNT(*) FROM analysis_history;  # 분석 기록 수
\q                           # 종료
```

---

## 🔧 문제 해결

### "데이터베이스 연결 실패" 오류

```bash
# Docker가 실행 중인지 확인
docker ps

# PostgreSQL 컨테이너가 없다면
docker start myskin-postgres

# 또는 새로 생성
docker run --name myskin-postgres -e POSTGRES_PASSWORD=myskin123 -e POSTGRES_DB=myskin -p 5432:5432 -d postgres:15
```

### 포트 5432가 이미 사용 중

다른 PostgreSQL이 실행 중일 수 있습니다:
```bash
# Windows
netstat -ano | findstr :5432

# 다른 포트 사용하려면 .env 수정
DATABASE_URL=postgresql://postgres:myskin123@localhost:5433/myskin
```

---

## 📚 자세한 문서

- [DATABASE_SETUP.md](DATABASE_SETUP.md) - 상세 설정 가이드
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API 문서

---

## 💡 주요 변경사항

### 이전 (JSON 파일)
```python
# data/history.json 파일에 저장
# data/users.json 파일에 저장
```

### 현재 (PostgreSQL)
```python
# PostgreSQL 데이터베이스에 저장
# 더 빠른 조회, 더 강력한 쿼리, 더 안전한 저장
```

### 파일 구조
```
MySkinProject/
├── models.py              # 데이터베이스 모델 정의
├── migrate_to_db.py       # 마이그레이션 스크립트
├── .env                   # 데이터베이스 URL 설정
├── DATABASE_SETUP.md      # 상세 설정 가이드
└── app.py                 # SQLAlchemy 사용하도록 업데이트됨
```

---

## 🎯 다음 단계

1. ✅ PostgreSQL 실행
2. ✅ 테이블 생성
3. ✅ 데이터 마이그레이션 (선택사항)
4. ✅ Flask 서버 실행
5. 📱 프론트엔드에서 테스트
6. 🚀 배포 준비

---

**문제가 있으신가요?**
- [DATABASE_SETUP.md](DATABASE_SETUP.md)의 트러블슈팅 섹션을 참고하세요
- 또는 이슈를 등록해주세요
