# MySkin LED Mask - Arduino Setup Guide

Seeed Xiao BLE (nRF52840) 보드를 사용한 LED 마스크 컨트롤러 설정 가이드

## 하드웨어 요구사항

1. **Seeed Xiao BLE (nRF52840)** 보드
2. **RGB LED 스트립** 또는 개별 RGB LED
3. **점퍼 와이어**
4. **USB-C 케이블** (프로그래밍 및 전원 공급용)

## 아두이노 IDE 설정

### 1. Arduino IDE 설치
- [Arduino IDE 다운로드](https://www.arduino.cc/en/software)
- Arduino IDE 2.x 이상 권장

### 2. Seeed nRF52 보드 지원 추가

1. Arduino IDE 열기
2. **파일 > 기본 설정** (Windows) 또는 **Arduino > Preferences** (Mac)
3. "추가적인 보드 매니저 URLs"에 다음 주소 추가:
   ```
   https://files.seeedstudio.com/arduino/package_seeeduino_boards_index.json
   ```
4. **확인** 클릭

### 3. 보드 매니저에서 nRF52 보드 설치

1. **도구 > 보드 > 보드 매니저**
2. "Seeed nRF52" 검색
3. **Seeed nRF52 Boards** 설치
4. 설치 완료 대기 (5-10분 소요 가능)

### 4. 필요한 라이브러리 설치

**ArduinoBLE 라이브러리:**
1. **스케치 > 라이브러리 포함하기 > 라이브러리 관리**
2. "ArduinoBLE" 검색
3. **ArduinoBLE by Arduino** 설치

## 하드웨어 연결

### LED 연결 (기본 설정)

```
Seeed Xiao BLE    →    RGB LED
-----------------      ----------
D2 (GPIO 2)       →    Red LED (또는 R 채널)
D3 (GPIO 3)       →    Green LED (또는 G 채널)
D4 (GPIO 4)       →    Blue LED (또는 B 채널)
GND               →    GND (공통)
3.3V              →    VCC (전원)
```

### 연결 주의사항

1. **전류 제한**: LED 밝기가 높으면 전류 소모가 큽니다. 필요시 외부 전원 사용
2. **저항 추가**: 개별 LED 사용 시 각 LED에 적절한 저항(220Ω~470Ω) 연결
3. **공통 GND**: 모든 부품은 공통 GND에 연결

### WS2812B LED 스트립 사용 시

WS2812B와 같은 디지털 LED 스트립 사용 시:
1. **FastLED** 또는 **Adafruit NeoPixel** 라이브러리 설치 필요
2. 코드 수정 필요 (별도 가이드 참조)

## 펌웨어 업로드

### 1. 보드 선택
- **도구 > 보드 > Seeed nRF52 Boards > Seeed XIAO BLE - nRF52840**

### 2. 포트 선택
- 보드를 USB로 연결
- **도구 > 포트** 에서 적절한 포트 선택
  - Windows: `COM3`, `COM4` 등
  - Mac: `/dev/cu.usbmodem...`
  - Linux: `/dev/ttyACM0` 등

### 3. 스케치 열기
- `MySkinLED_XiaoBLE.ino` 파일 열기

### 4. 업로드
- **업로드** 버튼 클릭 (→ 아이콘)
- 컴파일 및 업로드 완료 대기

### 5. 시리얼 모니터 확인
- **도구 > 시리얼 모니터** 열기
- Baud rate: **115200** 설정
- 정상 동작 시 메시지 확인:
  ```
  MySkin LED Mask - Xiao BLE
  Initializing...
  BLE LED Service started
  Device name: MySkin_LED_Mask
  Ready!
  Waiting for BLE connection...
  ```

## LED 핀 번호 변경

다른 핀을 사용하려면 코드 상단 수정:

```cpp
// Pin Definitions (adjust based on your hardware)
#define LED_PIN_R 2    // 원하는 핀 번호로 변경
#define LED_PIN_G 3
#define LED_PIN_B 4
```

사용 가능한 GPIO 핀:
- D0 ~ D10 (GPIO 0 ~ 10)
- A0 ~ A5 (아날로그 입력 가능)

## 문제 해결

### 1. 보드가 인식되지 않음
- USB 케이블 확인 (데이터 전송 지원 케이블 사용)
- 보드의 RESET 버튼을 2번 빠르게 누름 (부트로더 모드 진입)
- 다른 USB 포트 시도

### 2. 업로드 실패
- 시리얼 모니터가 열려있다면 닫기
- 보드 선택 및 포트 확인
- 부트로더 모드로 재진입 후 재시도

### 3. BLE 연결 안됨
- 시리얼 모니터에서 "BLE LED Service started" 메시지 확인
- 스마트폰/PC의 블루투스가 켜져있는지 확인
- 디바이스 이름 "MySkin_LED_Mask" 검색

### 4. LED가 켜지지 않음
- LED 극성 확인 (양극/음극)
- 연결 확인 (접촉 불량)
- 전원 공급 확인
- 시리얼 모니터에서 "LED Color set to..." 메시지 확인

## 테스트

### 시리얼 명령어로 테스트

시리얼 모니터에서 직접 명령 전송은 불가하지만, BLE 연결 후 Python API를 통해 테스트할 수 있습니다.

### 내장 LED 상태 표시

- **느린 깜빡임** (1초 간격): BLE 대기 중
- **계속 켜짐**: BLE 연결됨
- **빠른 깜빡임** (완료 후): 테라피 완료

## BLE 명령어 프로토콜

### 명령 형식

1. **테라피 시작**
   ```
   START:MODE:DURATION
   예: START:RED:20
   ```
   - MODE: RED, BLUE, GOLD
   - DURATION: 1~60 (분)

2. **테라피 중지**
   ```
   STOP
   ```

3. **상태 조회**
   ```
   STATUS
   ```

### 응답 형식

- `OK:STARTED:RED:20` - 시작 성공
- `OK:STOPPED` - 중지 완료
- `ACTIVE:RED:1200` - 진행 중 (남은 시간: 초)
- `IDLE` - 대기 중
- `COMPLETED` - 완료
- `ERROR:INVALID_MODE` - 오류

## LED 모드

| 모드 | 색상 | 파장 | 효과 |
|------|------|------|------|
| RED | 빨강 (255,0,0) | 630nm | 주름개선, 탄력증진, 콜라겐생성 |
| BLUE | 파랑 (0,0,255) | 415nm | 여드름완화, 모공진정, 피지조절 |
| GOLD | 금색 (255,215,0) | 590nm | 미백, 색소완화, 피부톤개선 |

## 참고 자료

- [Seeed Xiao BLE 공식 문서](https://wiki.seeedstudio.com/XIAO_BLE/)
- [ArduinoBLE 라이브러리 문서](https://www.arduino.cc/reference/en/libraries/arduinoble/)
- [nRF52840 데이터시트](https://infocenter.nordicsemi.com/index.jsp?topic=%2Fps_nrf52840%2Fkeyfeatures_html5.html)

## 지원

문제가 발생하면 시리얼 모니터 출력을 포함하여 이슈를 등록해주세요.
