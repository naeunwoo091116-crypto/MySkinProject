# BLE Mock 모드 가이드

## 개요

블루투스 어댑터가 없는 환경에서도 MySkin 프로젝트를 개발하고 테스트할 수 있도록 **Mock 모드**가 자동으로 활성화됩니다.

## Mock 모드란?

- 실제 BLE 하드웨어 없이 UI와 API를 테스트할 수 있는 시뮬레이션 모드
- 모든 BLE 통신을 가상으로 처리
- 실제 LED는 켜지지 않지만, 앱의 모든 기능을 테스트 가능

## 자동 전환

서버 시작 시 자동으로 환경을 감지합니다:

### 블루투스가 있는 경우
```
✅ 실제 BLE 서비스 사용
```
→ 실제 Seeed Xiao BLE 디바이스와 연결

### 블루투스가 없는 경우
```
⚠️ BLE Mock 모드 활성화 - 블루투스 없이도 UI 테스트 가능
   (실제 하드웨어 연결은 작동하지 않습니다)
```
→ Mock 서비스로 시뮬레이션

## Mock 모드 기능

### 1. 디바이스 스캔 시뮬레이션
```json
{
  "success": true,
  "devices": [
    {
      "name": "MySkin_LED_Mask",
      "address": "MOCK:E8:31:CD:12:34:56",
      "rssi": -45
    }
  ]
}
```

### 2. 연결 시뮬레이션
- Connect 버튼 클릭 → 즉시 연결 성공
- 연결 상태 UI 업데이트

### 3. 테라피 시작/중지 시뮬레이션
- START 명령 → 가상 타이머 시작
- STOP 명령 → 즉시 중지
- 상태 조회 → 남은 시간 시뮬레이션

### 4. 모든 메시지에 [MOCK] 표시
로그에서 Mock 모드임을 명확히 표시:
```
[MOCK] BLE 디바이스 스캔 시뮬레이션 (10초)
[MOCK] 디바이스 연결 성공: MOCK:E8:31:CD:12:34:56
[MOCK] 테라피 시작 시뮬레이션: red, 20분
```

## 사용 방법

### 서버 시작
```bash
cd C:\Users\user\Downloads\MySkinProject
venv1\Scripts\activate
python app.py
```

콘솔에서 모드 확인:
```
⚠️ BLE Mock 모드 활성화 - 블루투스 없이도 UI 테스트 가능
✅ 데이터베이스 연결 성공!
 * Running on http://127.0.0.1:5001
```

### 웹 브라우저에서 테스트

1. `http://localhost:5001` 접속
2. Connect 버튼 클릭
3. **[MOCK] 테라피가 시작되었습니다** 메시지 확인
4. UI의 모든 기능이 정상 작동

### Mock vs 실제 차이점

| 기능 | Mock 모드 | 실제 BLE |
|------|-----------|----------|
| 디바이스 스캔 | 가짜 디바이스 목록 | 실제 BLE 디바이스 검색 |
| 연결 | 즉시 성공 | 실제 GATT 연결 |
| LED 제어 | 시뮬레이션만 | 실제 LED 켜짐 |
| 상태 조회 | 가상 타이머 | 아두이노 실제 상태 |
| 로그 표시 | [MOCK] 접두사 | 일반 로그 |

## 개발 시나리오

### 시나리오 1: UI 개발
Mock 모드로 UI와 API 통신을 완벽하게 테스트할 수 있습니다.
- 버튼 동작
- 상태 표시
- 에러 처리
- 타이머 UI

### 시나리오 2: 하드웨어 통합
블루투스 어댑터를 구매하거나 다른 PC에서 실제 모드로 전환:
1. USB 블루투스 동글 연결
2. 서버 재시작
3. 자동으로 실제 BLE 서비스 활성화

## 실제 BLE로 전환

### 방법 1: 블루투스 어댑터 추가
1. USB Bluetooth 동글 구매 및 연결
2. Windows에서 블루투스 활성화
3. 서버 재시작
4. ✅ 실제 BLE 서비스 사용 메시지 확인

### 방법 2: 다른 PC 사용
1. 블루투스가 있는 노트북/PC에 프로젝트 복사
2. 가상환경 재생성:
   ```bash
   python -m venv venv1
   venv1\Scripts\activate
   pip install -r requirements.txt
   ```
3. 서버 실행

## Mock 모드 강제 활성화/비활성화

환경 변수로 강제 설정 가능:

### Mock 모드 강제 활성화
```bash
# Windows
set USE_BLE_MOCK=true
python app.py

# PowerShell
$env:USE_BLE_MOCK="true"
python app.py
```

### 실제 모드 강제 활성화
```bash
set USE_BLE_MOCK=false
python app.py
```

## 문제 해결

### Q: Mock 모드인데 연결이 안됩니다
A: 서버 로그를 확인하세요. Mock 모드에서는 항상 성공해야 합니다.

### Q: 실제 LED가 안 켜집니다
A: Mock 모드에서는 실제 하드웨어가 작동하지 않습니다. 이는 정상입니다.

### Q: 블루투스를 추가했는데 Mock 모드가 계속 나옵니다
A:
1. 서버를 완전히 종료하고 재시작
2. bleak 패키지 재설치: `pip install --force-reinstall bleak`
3. Python 재시작

## 로그 예시

### Mock 모드 시작
```
⚠️ BLE Mock 모드 활성화 - 블루투스 없이도 UI 테스트 가능
   (실제 하드웨어 연결은 작동하지 않습니다)
✅ 데이터베이스 연결 성공!
```

### Mock 연결
```
2026-01-06 18:10:00 - services.ble_service_mock - WARNING - ⚠️ Mock BLE Service 사용 중 - 실제 하드웨어 연결 없음
2026-01-06 18:10:00 - services.ble_service_mock - INFO - [MOCK] 디바이스 연결 시뮬레이션: MOCK:E8:31:CD:12:34:56
2026-01-06 18:10:01 - services.ble_service_mock - INFO - [MOCK] 디바이스 연결 성공
```

### Mock 테라피
```
2026-01-06 18:10:05 - services.ble_service_mock - INFO - [MOCK] 테라피 시작 시뮬레이션: red, 20분
```

## 정리

- ✅ **블루투스 없어도 개발 가능**
- ✅ **UI와 API 완전히 테스트 가능**
- ✅ **자동 모드 전환**
- ✅ **실제 모드와 동일한 API**
- ⚠️ **실제 LED는 작동하지 않음** (시뮬레이션만)

Mock 모드로 앱의 모든 기능을 개발하고, 나중에 하드웨어를 추가하면 자동으로 실제 모드로 전환됩니다!
