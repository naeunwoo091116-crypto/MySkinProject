# BLE 디바이스 연동 가이드

MySkin 프로젝트에 Seeed Xiao BLE 보드를 연동하는 방법

## 개요

이 프로젝트는 Seeed Xiao BLE (nRF52840) 보드를 사용하여 LED 테라피 마스크를 제어합니다.
Python 백엔드에서 BLE(Bluetooth Low Energy)를 통해 아두이노와 통신합니다.

## 아키텍처

```
[웹 브라우저]
    ↓ HTTP API
[Flask 백엔드 (Python)]
    ↓ BLE (bleak)
[Seeed Xiao BLE (Arduino)]
    ↓ GPIO PWM
[RGB LED 스트립/마스크]
```

## 사전 준비

### 1. 하드웨어 설정

아두이노 펌웨어 업로드는 `arduino/README.md`를 참조하세요.

### 2. Python 패키지 설치

```bash
# 가상환경 활성화
venv1\Scripts\activate  # Windows
source venv1/bin/activate  # Linux/Mac

# 의존성 설치
pip install -r requirements.txt
```

### 3. 필요한 패키지

- **bleak**: Python BLE 통신 라이브러리
- **asyncio**: 비동기 처리 (Python 3.7+ 내장)

## API 사용법

### 1. BLE 디바이스 스캔

주변 BLE 디바이스를 스캔합니다.

```bash
curl "http://localhost:5001/api/v1/ble/scan?timeout=10"
```

**응답 예시:**
```json
{
  "success": true,
  "devices": [
    {
      "name": "MySkin_LED_Mask",
      "address": "E8:31:CD:XX:XX:XX",
      "rssi": -45
    },
    {
      "name": "Unknown",
      "address": "AA:BB:CC:DD:EE:FF",
      "rssi": -67
    }
  ],
  "count": 2
}
```

### 2. BLE 디바이스 연결

특정 디바이스에 연결합니다.

```bash
curl -X POST http://localhost:5001/api/v1/ble/connect \
  -H "Content-Type: application/json" \
  -d '{"address": "E8:31:CD:XX:XX:XX"}'
```

**주소 없이 자동 연결** (MySkin_LED_Mask 자동 검색):
```bash
curl -X POST http://localhost:5001/api/v1/ble/connect \
  -H "Content-Type: application/json" \
  -d '{}'
```

**응답 예시:**
```json
{
  "success": true,
  "message": "디바이스 연결 성공",
  "address": "E8:31:CD:XX:XX:XX"
}
```

### 3. 디바이스 상태 조회

현재 디바이스 연결 상태 및 테라피 상태를 확인합니다.

```bash
curl http://localhost:5001/api/v1/ble/status
```

**응답 예시 (대기 중):**
```json
{
  "connected": true,
  "status": "idle",
  "message": "대기 중"
}
```

**응답 예시 (진행 중):**
```json
{
  "connected": true,
  "status": "active",
  "mode": "RED",
  "remaining_seconds": 720,
  "message": "테라피 진행 중"
}
```

### 4. LED 테라피 시작

LED 테라피를 시작합니다.

```bash
curl -X POST http://localhost:5001/api/v1/ble/therapy/start \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "red",
    "duration": 20
  }'
```

**파라미터:**
- `mode`: LED 모드 (red, blue, gold)
- `duration`: 지속 시간(분, 1-60)

**응답 예시:**
```json
{
  "success": true,
  "mode": "RED",
  "duration": 20,
  "message": "테라피가 시작되었습니다"
}
```

### 5. LED 테라피 중지

진행 중인 테라피를 중지합니다.

```bash
curl -X POST http://localhost:5001/api/v1/ble/therapy/stop
```

**응답 예시:**
```json
{
  "success": true,
  "message": "테라피가 중지되었습니다"
}
```

### 6. BLE 연결 해제

디바이스 연결을 해제합니다.

```bash
curl -X POST http://localhost:5001/api/v1/ble/disconnect
```

**응답 예시:**
```json
{
  "success": true,
  "message": "디바이스 연결 해제 완료"
}
```

## Python 코드 예제

### 직접 서비스 사용

```python
import asyncio
from services.ble_service import get_ble_service

async def main():
    ble = get_ble_service()

    # 디바이스 스캔
    devices = await ble.scan_devices(timeout=10)
    print(f"발견된 디바이스: {len(devices)}개")

    # 연결
    success = await ble.connect()
    if success:
        print("연결 성공!")

        # 테라피 시작
        result = await ble.start_therapy("red", 20)
        print(f"테라피 시작: {result}")

        # 상태 조회
        await asyncio.sleep(5)
        status = await ble.get_status()
        print(f"상태: {status}")

        # 연결 해제
        await ble.disconnect()
    else:
        print("연결 실패")

# 실행
asyncio.run(main())
```

## 통합 워크플로우

### 전체 프로세스 예시

1. **얼굴 분석 실행**
   ```bash
   curl -X POST http://localhost:5001/api/v1/analysis/face \
     -F "file=@face.jpg" \
     -F "user_id=test_user"
   ```

2. **분석 결과에서 LED 추천 확인**
   ```json
   {
     "recommendation": {
       "primary_mode": "red",
       "duration": 20,
       "reason": "주름과 탄력 개선 필요"
     }
   }
   ```

3. **BLE 디바이스 연결**
   ```bash
   curl -X POST http://localhost:5001/api/v1/ble/connect -H "Content-Type: application/json" -d '{}'
   ```

4. **추천된 테라피 시작**
   ```bash
   curl -X POST http://localhost:5001/api/v1/ble/therapy/start \
     -H "Content-Type: application/json" \
     -d '{"mode": "red", "duration": 20}'
   ```

5. **진행 상황 모니터링**
   ```bash
   # 주기적으로 상태 확인
   curl http://localhost:5001/api/v1/ble/status
   ```

## LED 모드 매핑

| 피부 문제 | 추천 모드 | 파장 | 효과 |
|-----------|-----------|------|------|
| 주름, 탄력저하 | RED | 630nm | 콜라겐 생성, 주름 개선 |
| 여드름, 모공 | BLUE | 415nm | 피지 조절, 여드름 완화 |
| 색소침착, 칙칙함 | GOLD | 590nm | 미백, 피부톤 개선 |

## 문제 해결

### BLE 스캔이 안됨

**증상:** 디바이스 스캔 시 아무것도 발견되지 않음

**해결:**
1. PC/서버의 블루투스가 켜져있는지 확인
2. 아두이노가 전원이 켜져있고 펌웨어가 정상 실행 중인지 확인
3. 시리얼 모니터에서 "BLE LED Service started" 메시지 확인
4. Windows의 경우 블루투스 권한 확인

### 연결은 되지만 명령이 안됨

**증상:** 연결은 성공하지만 테라피 시작 시 오류

**해결:**
1. BLE characteristic UUID 확인
2. 시리얼 모니터에서 명령 수신 로그 확인
3. 명령 형식이 올바른지 확인 (`START:MODE:DURATION`)

### 연결이 자주 끊김

**증상:** 연결 후 몇 초 뒤 자동으로 연결 해제

**해결:**
1. 거리 확인 (10m 이내)
2. 전파 간섭 최소화 (WiFi 공유기와 거리두기)
3. 아두이노 전원 안정성 확인

### Linux에서 권한 오류

**증상:** `Permission denied` 오류

**해결:**
```bash
# 블루투스 그룹에 사용자 추가
sudo usermod -a -G bluetooth $USER

# 재부팅 또는 재로그인
```

## 개발 팁

### 디버깅 모드

로그 레벨을 변경하여 상세한 디버그 정보 확인:

```python
# services/ble_service.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 타임아웃 조정

연결 타임아웃이나 스캔 시간 조정:

```python
# 스캔 시간 증가
devices = await ble.scan_devices(timeout=30)

# BleakClient 타임아웃 조정 (초 단위)
self.client = BleakClient(address, timeout=30.0)
```

### 여러 디바이스 관리

여러 LED 마스크를 동시에 제어하려면:
- 각 디바이스별로 별도의 `BLEDeviceService` 인스턴스 생성
- 디바이스 주소를 키로 하는 딕셔너리로 관리

## 보안 고려사항

1. **페어링**: 현재 페어링 없이 작동하지만, 필요시 BLE 페어링 추가 가능
2. **암호화**: BLE 연결은 기본적으로 암호화되지 않음. 민감한 데이터 전송 시 주의
3. **인증**: 프로덕션 환경에서는 디바이스 인증 메커니즘 추가 권장

## 성능 최적화

1. **연결 풀링**: 자주 연결/해제하는 대신 연결 유지
2. **배치 처리**: 여러 명령을 순차적으로 전송할 때 지연 최소화
3. **비동기 처리**: Flask에서 `async` 처리로 블로킹 방지

## 참고 자료

- [Bleak 공식 문서](https://bleak.readthedocs.io/)
- [BLE 프로토콜 개요](https://www.bluetooth.com/learn-about-bluetooth/bluetooth-technology/topology-options/le-audio/)
- [nRF52840 BLE 가이드](https://infocenter.nordicsemi.com/index.jsp?topic=%2Fcom.nordic.infocenter.sdk5.v15.0.0%2Fble_sdk_app_ble_app.html)

## API 엔드포인트 요약

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/ble/scan` | BLE 디바이스 스캔 |
| POST | `/api/v1/ble/connect` | 디바이스 연결 |
| POST | `/api/v1/ble/disconnect` | 연결 해제 |
| GET | `/api/v1/ble/status` | 상태 조회 |
| POST | `/api/v1/ble/therapy/start` | 테라피 시작 |
| POST | `/api/v1/ble/therapy/stop` | 테라피 중지 |
