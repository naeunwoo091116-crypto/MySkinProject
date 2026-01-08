# APK 디버깅 가이드

APK에서 문제가 발생할 때 콘솔 로그를 확인하는 방법입니다.

## 방법 1: Chrome Remote Debugging (권장)

### 1단계: USB 디버깅 활성화

**Android 휴대폰에서:**
1. 설정 → 휴대전화 정보
2. 빌드 번호를 7번 연속 탭
3. "개발자 모드 활성화됨" 메시지 확인
4. 설정 → 개발자 옵션
5. "USB 디버깅" 활성화

### 2단계: PC 연결

1. 휴대폰을 USB로 PC에 연결
2. "USB 디버깅 허용" 팝업에서 "허용" 클릭

### 3단계: Chrome DevTools 열기

**PC Chrome에서:**
1. 주소창에 `chrome://inspect` 입력
2. "Discover USB devices" 체크
3. 휴대폰에서 MySkin 앱 실행
4. Chrome에 앱이 나타나면 **"inspect"** 클릭

### 4단계: 콘솔 로그 확인

DevTools Console 탭에서 다음 로그 확인:

```
=== CONFIG 초기화 ===
APP_CONFIG exists: true
CONFIG.API_BASE_URL: http://192.168.219.93:5001
CONFIG.USER_ID: user_xxxxx

=== runAi 함수 호출됨 ===
API 호출 URL: http://192.168.219.93:5001/api/v1/analysis/face

=== connectBle 함수 호출됨 ===
BLE API 호출 URL: http://192.168.219.93:5001/api/v1/ble/connect
```

## 방법 2: Logcat (Android Studio)

### 1단계: Android Studio 실행

1. Android Studio 열기
2. 메뉴: View → Tool Windows → Logcat

### 2단계: 필터 설정

Logcat 검색창에:
```
package:com.myskin.app
```

### 3단계: 로그 확인

- `chromium` 태그로 필터링하면 JavaScript 로그 확인 가능
- 에러는 빨간색으로 표시됨

## 방법 3: ADB Logcat (명령어)

### 설치 확인
```bash
adb devices
```

출력:
```
List of devices attached
ABCD1234    device
```

### 로그 실시간 확인
```bash
adb logcat -s chromium:V
```

### 로그 파일로 저장
```bash
adb logcat > app_log.txt
```

## 예상되는 문제와 해결

### 문제 1: "APP_CONFIG exists: false"

**원인:** `config.js`가 로드되지 않음

**해결:**
```bash
# config.js 파일 존재 확인
ls mobile/www/js/config.js

# 다시 빌드
cd mobile
cordova build android
```

### 문제 2: "CONFIG.API_BASE_URL: ''" (빈 문자열)

**원인:** APP_CONFIG가 정의되지 않았거나 로드 순서 문제

**해결:**
1. Chrome DevTools Console에서 직접 확인:
   ```javascript
   APP_CONFIG
   CONFIG
   ```
2. 스크립트 로드 순서 확인

### 문제 3: "Failed to fetch" 에러

**원인:** 서버 연결 실패

**확인 사항:**
- [ ] Flask 서버 실행 중인지 확인
- [ ] 휴대폰과 PC가 같은 WiFi인지 확인
- [ ] 방화벽 설정 확인
- [ ] 휴대폰 브라우저에서 `http://192.168.219.93:5001` 접속 테스트

### 문제 4: 버튼 클릭해도 아무 반응 없음

**확인 사항:**
1. DevTools Console에서 에러 확인
2. 함수가 호출되는지 확인:
   ```javascript
   // Console에서 직접 실행
   connectBle()
   runAi()
   ```
3. `onclick` 이벤트가 등록되었는지 확인

## 빠른 테스트

Chrome DevTools Console에서 직접 실행:

```javascript
// CONFIG 확인
console.log('APP_CONFIG:', APP_CONFIG);
console.log('CONFIG:', CONFIG);

// API URL 테스트
fetch(CONFIG.API_BASE_URL + '/api/v1/device/modes')
  .then(r => r.json())
  .then(d => console.log('서버 응답:', d))
  .catch(e => console.error('서버 오류:', e));

// BLE 연결 테스트
connectBle();
```

## 디버그 APK 정보

현재 빌드된 APK에는 다음 디버깅 코드가 포함되어 있습니다:

1. ✅ CONFIG 초기화 로그
2. ✅ runAi() 호출 로그
3. ✅ connectBle() 호출 로그
4. ✅ API URL 출력

새 APK 위치:
```
C:\Users\naeun\Downloads\skin_care\MySkinProject\mobile\platforms\android\app\build\outputs\apk\debug\app-debug.apk
```

## 문제 해결 체크리스트

1. [ ] Flask 서버 실행됨 (`python app.py`)
2. [ ] 서버 출력에 `Running on http://192.168.219.93:5001` 표시됨
3. [ ] 휴대폰과 PC 같은 WiFi 연결됨
4. [ ] 휴대폰 브라우저에서 `http://192.168.219.93:5001` 접속 가능
5. [ ] APK 재설치 완료
6. [ ] 앱 권한 모두 허용됨
7. [ ] Chrome `chrome://inspect`에서 앱 연결됨
8. [ ] Console에 로그 출력됨

모든 항목이 체크되면 문제 원인을 찾을 수 있습니다!
