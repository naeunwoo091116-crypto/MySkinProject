# MySkin Mobile - 빠른 시작 가이드

## 5분 안에 APK 만들기

### 1단계: 사전 준비 (최초 1회)

#### Node.js 설치
```bash
# https://nodejs.org/ 에서 LTS 버전 다운로드 및 설치
node --version  # 확인
```

#### Cordova 설치
```bash
npm install -g cordova
cordova --version  # 확인
```

#### Android Studio 설치
1. https://developer.android.com/studio 에서 다운로드
2. 설치 시 "Android SDK", "Android SDK Platform-Tools" 선택
3. 설치 후 SDK Manager에서 추가 설치:
   - Android 13.0 (API 33)
   - Android SDK Build-Tools

#### 환경 변수 설정 (Windows)
```powershell
# PowerShell 관리자 권한으로 실행
setx ANDROID_HOME "C:\Users\[사용자명]\AppData\Local\Android\Sdk"
# 재부팅 또는 새 터미널 열기
```

### 2단계: 프로젝트 설정

```bash
# mobile 폴더로 이동
cd mobile

# 의존성 설치
npm install

# Android 플랫폼 추가
cordova platform add android

# 플러그인 설치
npm run install:plugins
```

### 3단계: www 폴더 준비

```bash
# Python 스크립트로 자동 변환
python prepare_www.py
```

### 4단계: Flask 서버 실행

```bash
# 새 터미널 열기
cd ..
venv1\Scripts\activate
python app.py
```

서버가 `http://localhost:5001`에서 실행되는지 확인

### 5단계: APK 빌드

#### 옵션 A: 에뮬레이터에서 테스트
```bash
# Android Studio AVD Manager에서 에뮬레이터 실행
# mobile 폴더에서:
npm run android:run
```

#### 옵션 B: APK 파일 생성
```bash
npm run android:build

# APK 위치:
# platforms/android/app/build/outputs/apk/debug/app-debug.apk
```

### 6단계: 실제 기기에서 테스트

#### APK 설치
1. `app-debug.apk` 파일을 휴대폰으로 전송
2. 파일 탐색기에서 APK 클릭
3. "알 수 없는 출처" 허용 후 설치

#### 네트워크 설정
PC와 휴대폰을 **같은 WiFi**에 연결:

1. PC의 IP 주소 확인:
```bash
ipconfig  # Windows
# WiFi 어댑터의 IPv4 주소 확인 (예: 192.168.0.10)
```

2. `www/js/config.js` 수정:
```javascript
API_BASE_URL: 'http://192.168.0.10:5001',  // PC IP로 변경
```

3. Flask 서버를 모든 인터페이스에서 실행:
```python
# app.py 마지막 부분:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

4. 다시 빌드:
```bash
npm run android:build
```

## 문제 해결

### "Cordova가 설치되지 않았습니다"
```bash
npm install -g cordova
```

### "ANDROID_HOME이 설정되지 않았습니다"
```bash
# Windows
setx ANDROID_HOME "C:\Users\[사용자명]\AppData\Local\Android\Sdk"

# 터미널 재시작 후 확인
echo %ANDROID_HOME%
```

### "서버에 연결할 수 없습니다"
- 에뮬레이터: `API_BASE_URL: 'http://10.0.2.2:5001'` 사용
- 실제 기기: PC IP 주소로 변경 + 같은 WiFi 연결 확인
- 방화벽: Windows 방화벽에서 Python 허용

### "권한이 거부되었습니다" (BLE/카메라)
- 앱 설정 > 권한에서 수동으로 허용
- Android 12 이상: 위치 권한도 필요 (BLE 스캔용)

## 다음 단계

✅ **기본 기능 확인**
- 카메라로 사진 촬영
- Flask API로 피부 분석
- BLE 디바이스 연결

✅ **UI/UX 개선**
- 앱 아이콘 교체
- 스플래시 스크린 커스터마이징
- 색상/폰트 변경

✅ **배포 준비**
- 릴리즈 APK 생성
- Google Play Console 등록
- 앱 설명/스크린샷 준비

## 자주 묻는 질문

**Q: Flask 서버 없이 APK만 배포할 수 있나요?**
A: 아니오. 현재 구조는 백엔드 서버가 필요합니다. 서버를 클라우드(AWS, Google Cloud 등)에 배포하세요.

**Q: iOS 버전도 만들 수 있나요?**
A: 네, Cordova는 iOS도 지원합니다. Mac + Xcode가 필요합니다.

**Q: 오프라인에서도 동작하나요?**
A: 현재는 서버 연결이 필수입니다. 오프라인 지원을 원하면 Service Worker + 로컬 AI 모델 통합이 필요합니다.

**Q: 앱 크기가 얼마나 되나요?**
A: 약 5-10MB (플러그인 포함). AI 모델을 앱에 포함하면 100MB 이상 될 수 있습니다.

## 도움이 필요하면

1. `mobile/README.md` 상세 문서 참고
2. Cordova 공식 문서: https://cordova.apache.org/docs/
3. GitHub Issues: 프로젝트 저장소에 이슈 등록
