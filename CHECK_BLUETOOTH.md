# 블루투스 문제 해결 가이드

## 현재 오류
```
No Bluetooth adapter found
```

서버를 실행하는 PC에 블루투스 어댑터가 없거나 비활성화되어 있습니다.

## 해결 방법

### 1. Windows 블루투스 확인

#### 방법 A: 설정에서 확인
1. **Windows 설정** 열기 (Win + I)
2. **장치** > **Bluetooth 및 기타 장치**
3. **Bluetooth** 스위치가 "켜짐"인지 확인

#### 방법 B: 장치 관리자 확인
1. **장치 관리자** 열기 (Win + X > 장치 관리자)
2. **Bluetooth** 항목 확인
3. 비활성화되어 있다면 우클릭 > **사용**

### 2. 블루투스 어댑터가 없는 경우

#### 옵션 A: USB 블루투스 동글 구매
- USB Bluetooth 5.0 어댑터 권장
- 가격: 약 1만원 내외
- 설치 후 드라이버 자동 설치

#### 옵션 B: 다른 PC/노트북 사용
- 블루투스가 있는 다른 PC에서 서버 실행
- 프로젝트 폴더를 USB나 클라우드로 이동

### 3. Windows에서 블루투스 서비스 확인

PowerShell (관리자 권한)에서 실행:

```powershell
# 블루투스 서비스 상태 확인
Get-Service bthserv

# 블루투스 서비스 시작
Start-Service bthserv

# 블루투스 서비스 자동 시작 설정
Set-Service bthserv -StartupType Automatic
```

### 4. 임시 해결책: 시뮬레이션 모드

블루투스가 없어도 개발을 계속하려면 시뮬레이션 모드를 사용할 수 있습니다.

## 시뮬레이션 모드 사용 (블루투스 없이 개발)

BLE 디바이스 없이도 UI와 API를 테스트할 수 있는 Mock 버전을 제공합니다.
