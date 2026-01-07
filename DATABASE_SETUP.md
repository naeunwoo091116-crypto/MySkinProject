# PostgreSQL 데이터베이스 설정 가이드

## 📋 개요
이 문서는 MySkin 프로젝트를 JSON 파일 저장에서 PostgreSQL 데이터베이스로 마이그레이션하는 전체 과정을 설명합니다.

---

## 1️⃣ PostgreSQL 설치

### 방법 A: Docker 사용 (추천)

**장점:**
- 설치가 간단하고 깔끔
- 여러 버전 관리 용이
- 삭제도 간편

**설치 단계:**

```bash
# 1. PostgreSQL 컨테이너 실행
docker run --name myskin-postgres \
  -e POSTGRES_PASSWORD=myskin123 \
  -e POSTGRES_DB=myskin \
  -p 5432:5432 \
  -d postgres:15

# 2. 컨테이너 상태 확인
docker ps

# 3. PostgreSQL 접속 테스트
docker exec -it myskin-postgres psql -U postgres -d myskin

# 4. 접속 후 테스트 쿼리
\dt                    # 테이블 목록 확인
\q                     # 종료
```

**컨테이너 관리 명령어:**
```bash
# 컨테이너 시작
docker start myskin-postgres

# 컨테이너 중지
docker stop myskin-postgres

# 컨테이너 삭제 (데이터도 삭제됨)
docker rm -f myskin-postgres

# 로그 확인
docker logs myskin-postgres
```

---

### 방법 B: Windows 직접 설치

**설치 단계:**

1. PostgreSQL 다운로드
   - https://www.postgresql.org/download/windows/
   - PostgreSQL 15 이상 권장

2. 설치 중 설정:
   - Password: `myskin123` (또는 원하는 비밀번호)
   - Port: `5432` (기본값)
   - Locale: 한국어 (선택사항)

3. 데이터베이스 생성:
```sql
-- pgAdmin 또는 psql에서 실행
CREATE DATABASE myskin;
```

4. 환경변수 확인:
   - `PATH`에 PostgreSQL bin 경로 추가 확인
   - 예: `C:\Program Files\PostgreSQL\15\bin`

---

## 2️⃣ 환경 설정

### .env 파일 수정

프로젝트 루트에 `.env` 파일이 생성되어 있습니다. 필요시 수정:

```bash
# Docker 사용 시 (기본값)
DATABASE_URL=postgresql://postgres:myskin123@localhost:5432/myskin

# 비밀번호를 변경했다면
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/myskin

# 원격 서버 사용 시
DATABASE_URL=postgresql://username:password@hostname:5432/database_name
```

**URL 형식:**
```
postgresql://[사용자명]:[비밀번호]@[호스트]:[포트]/[데이터베이스명]
```

---

## 3️⃣ Python 패키지 설치

```bash
# 프로젝트 디렉토리에서 실행
pip install -r requirements.txt

# 또는 개별 설치
pip install sqlalchemy psycopg2-binary python-dotenv
```

**설치 확인:**
```python
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
python -c "import psycopg2; print(psycopg2.__version__)"
```

---

## 4️⃣ 데이터베이스 테이블 생성

### 방법 1: models.py 직접 실행

```bash
python models.py
```

**출력 예시:**
```
Creating database tables...
2024-01-05 ... CREATE TABLE users ...
2024-01-05 ... CREATE TABLE analysis_history ...
✅ Database tables created successfully!
```

### 방법 2: Python 인터랙티브 쉘

```python
python
>>> from models import init_db
>>> init_db()
✅ Database tables created successfully!
```

### 테이블 구조 확인

PostgreSQL에 접속하여 테이블 확인:

```bash
# Docker 사용 시
docker exec -it myskin-postgres psql -U postgres -d myskin

# 로컬 설치 시
psql -U postgres -d myskin
```

```sql
-- 테이블 목록 확인
\dt

-- users 테이블 구조
\d users

-- analysis_history 테이블 구조
\d analysis_history

-- 샘플 쿼리
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM analysis_history;
```

---

## 5️⃣ 기존 데이터 마이그레이션

JSON 파일에 기존 데이터가 있다면 PostgreSQL로 이전:

```bash
python migrate_to_db.py
```

**출력 예시:**
```
🚀 MySkin 프로젝트 데이터 마이그레이션
   JSON → PostgreSQL
============================================================

1️⃣ 데이터베이스 테이블 생성 중...
✅ 테이블 생성 완료!

👤 사용자 프로필 마이그레이션 시작
✅ 추가됨: user_abc123 - 김수지
✅ 사용자 마이그레이션 완료: 1명

📝 분석 히스토리 마이그레이션 시작
✅ 추가됨: user_abc123 - 점수 82 - 2024-01-15
✅ 히스토리 마이그레이션 완료: 15개 추가, 0개 건너뜀

🔍 마이그레이션 검증
📊 데이터베이스 현황:
   - 사용자: 1명
   - 분석 기록: 15개

✅ 마이그레이션 완료!
```

---

## 6️⃣ Flask 서버 실행

```bash
python app.py
```

**정상 실행 시 출력:**
```
✅ 데이터베이스 연결 성공!
--- AI 모델 로딩 시작 (부위별 설정 적용) ---
🔄 로딩 중: forehead (Class:4, Reg:15)
✅ forehead 로드 성공!
...
 * Running on http://localhost:5000
```

---

## 7️⃣ API 테스트

### 히스토리 조회 테스트

```bash
# Windows PowerShell
Invoke-WebRequest -Uri "http://localhost:5000/api/v1/history/user_abc123" -Method GET

# 또는 브라우저에서
http://localhost:5000/api/v1/history/user_abc123
```

### Python으로 테스트

```python
import requests

# 히스토리 조회
response = requests.get('http://localhost:5000/api/v1/history/user_abc123')
print(response.json())

# 통계 조회
response = requests.get('http://localhost:5000/api/v1/stats/user_abc123')
print(response.json())
```

---

## 🔧 트러블슈팅

### 문제 1: "데이터베이스 연결 실패"

**증상:**
```
⚠️ 데이터베이스 초기화 오류: could not connect to server
```

**해결방법:**
```bash
# 1. PostgreSQL 실행 확인
docker ps  # Docker 사용 시
# 또는
netstat -an | findstr 5432  # Windows

# 2. .env 파일 DATABASE_URL 확인
# 3. 방화벽 설정 확인
```

---

### 문제 2: "모듈을 찾을 수 없음"

**증상:**
```
ModuleNotFoundError: No module named 'sqlalchemy'
```

**해결방법:**
```bash
pip install sqlalchemy psycopg2-binary python-dotenv
```

---

### 문제 3: "테이블이 이미 존재함"

**증상:**
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.DuplicateTable)
```

**해결방법:**
이미 테이블이 생성되어 있으므로 정상입니다. 무시하고 진행하세요.

테이블을 재생성하려면:
```sql
-- PostgreSQL에 접속하여 실행
DROP TABLE analysis_history;
DROP TABLE users;

-- 그 후 다시 models.py 실행
python models.py
```

---

### 문제 4: "중복 데이터"

마이그레이션 스크립트는 중복을 자동으로 건너뜁니다.
강제로 재마이그레이션하려면:

```sql
-- 기존 데이터 삭제
TRUNCATE TABLE analysis_history;
TRUNCATE TABLE users;

-- 다시 마이그레이션
python migrate_to_db.py
```

---

## 📊 데이터베이스 스키마

### users 테이블
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100),
    skin_type VARCHAR(50),
    concerns JSON,
    goals TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### analysis_history 테이블
```sql
CREATE TABLE analysis_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    overall_score INTEGER,
    regions JSON NOT NULL,
    recommendation JSON,
    course_name VARCHAR(100) DEFAULT 'AI 정밀 분석'
);

CREATE INDEX idx_history_user_id ON analysis_history(user_id);
CREATE INDEX idx_history_timestamp ON analysis_history(timestamp);
```

---

## 🎯 다음 단계

1. **백업 설정**
   ```bash
   # PostgreSQL 백업
   docker exec myskin-postgres pg_dump -U postgres myskin > backup.sql

   # 복원
   docker exec -i myskin-postgres psql -U postgres myskin < backup.sql
   ```

2. **운영 환경 설정**
   - 비밀번호 강화
   - SSL 연결 활성화
   - 정기 백업 자동화

3. **성능 최적화**
   - 인덱스 추가
   - 쿼리 최적화
   - 연결 풀링 설정

---

## 📞 문의

문제가 발생하면:
1. 로그 확인: `docker logs myskin-postgres`
2. Flask 로그 확인
3. PostgreSQL 로그 확인: `/var/log/postgresql/`
