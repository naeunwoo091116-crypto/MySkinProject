# USB 시리얼 연결 가이드

## 개요

**블루투스 없이 USB 케이블로 Seeed Xiao BLE와 직접 연결!**

이 가이드는 USB 케이블을 사용하여 Seeed Xiao BLE 보드와 PC를 직접 연결하는 방법을 설명합니다.

## 장점

✅ **블루투스 어댑터 불필요** - USB 포트만 있으면 OK
✅ **안정적인 연결** - 무선 간섭 없음
✅ **빠른 응답속도** - 직접 연결로 지연 최소화
✅ **개발 편의성** - 시리얼 모니터로 디버깅 가능

## 필요한 것

1. **Seeed Xiao BLE 보드**
2. **USB-C 케이블** (데이터 전송 지원)
3. **PC의 USB 포트**

## 설치 단계

### 1. 패키지 설치

```bash
cd C:\Users\user\Downloads\MySkinProject
venv1\Scripts\activate
pip install pyserial
```

### 2. 아두이노 펌웨어 업로드

`arduino/MySkinLED_XiaoBLE/MySkinLED_XiaoBLE.ino` 파일을 업로드합니다.

**중요**: 최신 버전은 USB 시리얼과 BLE를 모두 지원합니다!

```
Arduino IDE에서:
1. 파일 > 열기 > MySkinLED_XiaoBLE.ino
2. 도구 > 보드 > Seeed XIAO BLE - nRF52840
3. 도구 > 포트 > COM포트 선택
4. 업로드 버튼 클릭
```

### 3. 드라이버 확인 (Windows)

Seeed Xiao BLE는 보통 자동으로 인식되지만, 안될 경우:

1. **장치 관리자** 열기 (Win + X > 장치 관리자)
2. **포트 (COM & LPT)** 확인
3. "USB Serial Device" 또는 "Arduino" 항목 확인

드라이버 필요 시: [CH340 드라이버](http://www.wch.cn/downloads/CH341SER_ZIP.html)

## 사용 방법

### 자동 연결

1. **Seeed Xiao BLE를 USB로 PC에 연결**
2. **서버 시작**

```bash
cd C:\Users\user\Downloads\MySkinProject
venv1\Scripts\activate
python app.py
```

3. **연결 모드 확인**

콘솔에 다음 메시지가 표시되면 성공:

```
✅ USB 시리얼 모드 사용 (유선 연결)
📡 현재 연결 모드: SERIAL
✅ 데이터베이스 연결 성공!
```

4. **웹 브라우저에서 테스트**

- `http://localhost:5001` 접속
- **Connect** 버튼 클릭
- 자동으로 USB 포트 검색 및 연결
- "디바이스 연결 성공 (SERIAL 모드)" 메시지 확인

## 수동 포트 선택

특정 포트를 지정하려면 API 호출 시 포트 이름 전달:

```bash
# PowerShell
$body = @{
    port = "COM3"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5001/api/v1/ble/connect" `
    -Method Post -ContentType "application/json" -Body $body
```

## 포트 확인 방법

### Windows

**방법 1: 장치 관리자**
```
1. Win + X > 장치 관리자
2. 포트 (COM & LPT) 항목 확인
3. 예: "USB Serial Device (COM3)"
```

**방법 2: PowerShell**
```powershell
Get-WmiObject Win32_SerialPort | Select Name,DeviceID
```

**방법 3: Python**
```python
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"{port.device}: {port.description}")
```

### Mac/Linux

```bash
# Mac
ls /dev/cu.*

# Linux
ls /dev/ttyUSB* /dev/ttyACM*
```

## 연결 우선순위

서버 시작 시 자동으로 다음 순서로 연결 시도:

1. **USB 시리얼** (최우선)
2. **BLE 무선** (블루투스가 있을 경우)
3. **Mock 모드** (모두 실패 시)

## API 엔드포인트

USB 시리얼 모드에서도 동일한 API 사용:

| Endpoint | 설명 |
|----------|------|
| `GET /api/v1/ble/scan` | 시리얼 포트 스캔 |
| `POST /api/v1/ble/connect` | 포트 연결 |
| `POST /api/v1/ble/disconnect` | 연결 해제 |
| `GET /api/v1/ble/status` | 상태 조회 |
| `POST /api/v1/ble/therapy/start` | 테라피 시작 |
| `POST /api/v1/ble/therapy/stop` | 테라피 중지 |

## 시리얼 모니터로 디버깅

Arduino IDE의 시리얼 모니터로 실시간 로그 확인 가능:

```
도구 > 시리얼 모니터 (Ctrl+Shift+M)
Baud Rate: 115200
```

**예상 출력:**
```
MySkin LED Mask - Xiao BLE
Initializing...
BLE LED Service started
Ready!
Serial command received: START:RED:20
OK:STARTED:RED:20
LED Color set to R:255 G:0 B:0
```

## 문제 해결

### Q: "No module named 'serial'" 오류
A: pyserial 설치 필요
```bash
pip install pyserial
```

### Q: 포트를 찾을 수 없습니다
A:
1. USB 케이블이 데이터 전송을 지원하는지 확인
2. Seeed Xiao BLE가 PC에 인식되는지 확인
3. 다른 USB 포트 시도

### Q: "Access denied" 또는 "Permission denied"
A:
- **Windows**: 다른 프로그램(Arduino IDE, 시리얼 모니터 등)이 포트를 사용 중이면 닫기
- **Linux**: 사용자를 dialout 그룹에 추가
  ```bash
  sudo usermod -a -G dialout $USER
  # 로그아웃 후 재로그인
  ```

### Q: 연결되지만 명령이 작동하지 않음
A:
1. 아두이노에 최신 펌웨어 업로드 확인
2. 시리얼 모니터에서 "Serial command received" 메시지 확인
3. Baud rate 확인 (115200)

### Q: Mock 모드로 계속 실행됨
A:
1. USB 케이블이 PC에 연결되어 있는지 확인
2. 아두이노가 전원이 켜져있는지 확인 (내장 LED 확인)
3. 서버 재시작

## 연결 모드 비교

| 모드 | 장점 | 단점 | 사용 시나리오 |
|------|------|------|--------------|
| **USB 시리얼** | 안정적, 빠름, 디버깅 가능 | 케이블 필요 | 개발, 데스크탑 사용 |
| **BLE 무선** | 무선, 이동 자유 | 블루투스 필요, 간섭 가능 | 모바일, 이동형 사용 |
| **Mock 모드** | 하드웨어 불필요 | 실제 LED 작동 안함 | UI 개발, 테스트 |

## 예제: 전체 워크플로우

### 1. 연결
```bash
# 서버 시작
python app.py

# 출력 확인
✅ USB 시리얼 모드 사용 (유선 연결)
```

### 2. 웹에서 사용
```
http://localhost:5001
→ Connect 버튼 클릭
→ "디바이스 연결 성공 (SERIAL 모드)"
```

### 3. LED 제어
```
기기 관리 탭 → 모드 선택 (RED/BLUE/GOLD)
→ 지속 시간 설정
→ Start 버튼
```

### 4. 시리얼 모니터 확인
```
Serial command received: START:RED:20
OK:STARTED:RED:20
Starting therapy: RED for 20 minutes
LED Color set to R:255 G:0 B:0
```

### 5. 상태 확인
```
기기 관리 탭에서 진행 상황 확인
또는 API: GET /api/v1/ble/status
```

## 고급 사용

### Python에서 직접 제어

```python
from services.serial_service import get_serial_service

# 서비스 획득
serial_service = get_serial_service()

# 연결
success = serial_service.connect()  # 자동 포트 검색
# 또는
success = serial_service.connect("COM3")  # 특정 포트

if success:
    # LED 시작
    result = serial_service.start_therapy("red", 20)
    print(result)

    # 상태 조회
    status = serial_service.get_status()
    print(status)

    # 중지
    serial_service.stop_therapy()

    # 연결 해제
    serial_service.disconnect()
```

### 명령어 직접 전송

```python
# 원시 명령 전송
response = serial_service.send_command("START:BLUE:15")
print(response)  # OK:STARTED:BLUE:15
```

## 정리

- ✅ **블루투스 없어도 OK** - USB만 있으면 실제 하드웨어 제어 가능
- ✅ **자동 감지** - 서버 시작 시 자동으로 USB 모드 활성화
- ✅ **동일한 API** - BLE와 동일한 API 사용
- ✅ **안정적** - 유선 연결로 안정성 최대화
- ✅ **디버깅 편리** - 시리얼 모니터로 실시간 로그 확인

USB 케이블로 연결하고 서버를 시작하면 자동으로 작동합니다!
