# 서버 재시작 가이드

## 변경 사항
- BLE API 엔드포인트를 Blueprint로 등록
- `/api/v1/ble/*` 엔드포인트가 정상적으로 작동하도록 수정

## 재시작 방법

### Windows
```bash
# 1. 현재 실행 중인 서버 중지 (Ctrl+C)

# 2. 가상환경 활성화 (이미 활성화되어 있으면 생략)
cd C:\Users\user\Downloads\MySkinProject
venv1\Scripts\activate

# 3. 서버 재시작
python app.py
```

### 확인 사항
서버 시작 시 다음 메시지가 표시되어야 합니다:
```
✅ 데이터베이스 연결 성공!
 * Running on http://127.0.0.1:5001
```

## 테스트

### 1. 브라우저에서 확인
```
http://localhost:5001
```

### 2. BLE 연결 테스트
1. 우측 상단 "Connect" 버튼 클릭
2. 콘솔에서 연결 시도 로그 확인
3. 연결 성공 시 "Connected"로 변경

### 3. API 직접 테스트 (PowerShell)
```powershell
# BLE 상태 확인
Invoke-RestMethod -Uri "http://localhost:5001/api/v1/ble/status" -Method Get

# BLE 연결
Invoke-RestMethod -Uri "http://localhost:5001/api/v1/ble/connect" -Method Post -ContentType "application/json" -Body "{}"
```

## 문제 해결

### 404 오류가 계속 발생하는 경우
1. 서버 완전히 종료 (Ctrl+C)
2. Python 프로세스 확인 및 종료
   ```bash
   # Windows
   tasklist | findstr python
   taskkill /F /PID <프로세스ID>
   ```
3. 서버 재시작

### Import 오류 발생 시
```bash
# 필요한 패키지 재설치
pip install -r requirements.txt
```

### BLE 라이브러리 오류
```bash
# bleak 재설치
pip uninstall bleak
pip install bleak
```

## 정상 작동 확인

### 서버 로그에서 확인해야 할 내용
```
✅ 데이터베이스 연결 성공!
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5001
```

### Connect 버튼 클릭 시
```
BLE 디바이스 연결 중... (프론트엔드)
127.0.0.1 - - [날짜] "POST /api/v1/ble/connect HTTP/1.1" 200 - (서버 로그)
```

### 연결 성공 시
```
INFO:services.ble_service:BLE 디바이스 스캔 시작
INFO:services.ble_service:MySkin 디바이스 발견: XX:XX:XX:XX:XX:XX
INFO:services.ble_service:디바이스 연결 성공
```
