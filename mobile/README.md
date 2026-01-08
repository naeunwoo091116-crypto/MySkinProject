# MySkin Mobile - Cordova 앱

Flask 웹앱을 Android APK로 변환한 Cordova 프로젝트입니다.

## 사전 요구사항

### 필수 설치
```bash
# Node.js 설치 (v16 이상)
# https://nodejs.org/

# Cordova CLI 설치
npm install -g cordova

# Android Studio 설치
# https://developer.android.com/studio

# Java JDK 설치 (JDK 11 권장)
# Android Studio > Settings > Build Tools > Gradle JDK
```

### 환경 변수 설정 (Windows)
```bash
# ANDROID_HOME 설정
setx ANDROID_HOME "C:\Users\[사용자명]\AppData\Local\Android\Sdk"

# PATH에 추가
setx PATH "%PATH%;%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\tools"
```

## 프로젝트 설정

### 1. 의존성 설치
```bash
cd mobile
npm install
```

### 2. Android 플랫폼 추가
```bash
cordova platform add android
```

### 3. 플러그인 설치
```bash
npm run install:plugins
```

또는 수동 설치:
```bash
cordova plugin add cordova-plugin-camera
cordova plugin add cordova-plugin-file
cordova plugin add cordova-plugin-ble-central
cordova plugin add cordova-plugin-device
cordova plugin add cordova-plugin-whitelist
cordova plugin add cordova-plugin-inappbrowser
```

### 4. www 폴더 준비
```bash
# Python 스크립트로 자동 변환
python prepare_www.py
```

수동 변환:
1. `../templates/index.html`을 `www/index.html`로 복사
2. `<head>` 태그 안에 다음 추가:
```html
<script type="text/javascript" src="cordova.js"></script>
<script type="text/javascript" src="js/config.js"></script>
<script type="text/javascript" src="js/camera.js"></script>
<script type="text/javascript" src="js/ble.js"></script>
```

### 5. API 서버 URL 설정
`www/js/config.js` 파일에서 서버 주소 변경:

```javascript
const APP_CONFIG = {
    // 안드로이드 에뮬레이터
    API_BASE_URL: 'http://10.0.2.2:5001',

    // 실제 기기 (WiFi 연결 시)
    // API_BASE_URL: 'http://192.168.0.10:5001',

    // 배포용 (실제 서버)
    // API_BASE_URL: 'https://your-server.com',
    // ...
};
```

### 6. Flask 서버 실행
```bash
# 별도 터미널에서 백엔드 서버 실행
cd ..
venv1\Scripts\activate  # Windows
python app.py
```

## 빌드 및 실행

### 에뮬레이터에서 실행
```bash
# Android 에뮬레이터 실행 (Android Studio AVD Manager)
npm run android:run
```

### APK 빌드 (디버그)
```bash
npm run android:build

# 출력: platforms/android/app/build/outputs/apk/debug/app-debug.apk
```

### APK 빌드 (릴리즈)
```bash
# 키스토어 생성 (최초 1회)
keytool -genkey -v -keystore myskin.keystore -alias myskin -keyalg RSA -keysize 2048 -validity 10000

# 릴리즈 빌드
npm run android:build:release

# APK 서명
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore myskin.keystore platforms/android/app/build/outputs/apk/release/app-release-unsigned.apk myskin

# zipalign
zipalign -v 4 platforms/android/app/build/outputs/apk/release/app-release-unsigned.apk MySkin-release.apk
```

## 주요 파일 구조

```
mobile/
├── config.xml              # Cordova 앱 설정 (권한, 플랫폼, 플러그인)
├── package.json            # Node.js 의존성 및 빌드 스크립트
├── prepare_www.py          # HTML 변환 스크립트
├── www/                    # 앱 소스 코드
│   ├── index.html          # 메인 HTML (Flask template에서 변환)
│   ├── js/
│   │   ├── config.js       # API URL, BLE 설정
│   │   ├── camera.js       # Cordova 카메라 래퍼
│   │   └── ble.js          # Cordova BLE 래퍼
│   ├── css/
│   └── img/
└── platforms/              # 플랫폼별 빌드 파일 (자동 생성)
```

## 카메라 사용법

```javascript
// 카메라 촬영
cordovaCamera.takePicture()
    .then(imageDataURL => {
        // imageDataURL: "data:image/jpeg;base64,..."
        console.log('사진 촬영 완료');
    })
    .catch(error => {
        console.error('카메라 오류:', error);
    });

// 갤러리에서 선택
cordovaCamera.selectFromGallery()
    .then(imageDataURL => {
        console.log('사진 선택 완료');
    });

// Flask API로 분석 요청
cordovaCamera.uploadImage(imageDataURL, 'user123')
    .then(result => {
        console.log('분석 결과:', result);
    });
```

## BLE 사용법

```javascript
// BLE 디바이스 스캔
cordovaBLE.scan(10)  // 10초간 스캔
    .then(devices => {
        console.log('발견된 디바이스:', devices);
        if (devices.length > 0) {
            return cordovaBLE.connect(devices[0].id);
        }
    })
    .then(() => {
        // LED 모드 실행 (RED, 20분)
        return cordovaBLE.sendLEDCommand('RED', 20);
    })
    .then(() => {
        console.log('LED 시작됨');
    })
    .catch(error => {
        console.error('BLE 오류:', error);
    });
```

## 문제 해결

### 1. "cordova: command not found"
```bash
npm install -g cordova
```

### 2. "Android SDK not found"
```bash
# Android Studio 설치 후 SDK Manager에서 다음 설치:
# - Android SDK Platform-Tools
# - Android SDK Build-Tools
# - Android 13.0 (API 33)
```

### 3. 서버 연결 오류
- 에뮬레이터: `10.0.2.2:5001` 사용
- 실제 기기: PC와 같은 WiFi 네트워크에 연결 후 PC IP 주소 사용
- Flask 서버가 `0.0.0.0:5001`로 실행되고 있는지 확인

### 4. BLE 권한 오류 (Android 12+)
`config.xml`에 다음 권한 확인:
```xml
<uses-permission android:name="android.permission.BLUETOOTH_SCAN" />
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
```

### 5. 카메라 권한 오류
앱 최초 실행 시 권한 요청 팝업이 나타나야 합니다. 설정에서 수동으로 권한 부여 가능.

## 배포 체크리스트

- [ ] `www/js/config.js`에서 실제 서버 URL로 변경
- [ ] `config.xml`에서 버전 번호 업데이트
- [ ] 앱 아이콘 교체 (`res/icon/android/*.png`)
- [ ] 스플래시 스크린 교체 (`res/screen/android/*.png`)
- [ ] 릴리즈 APK 빌드 및 서명
- [ ] Google Play Console에 업로드

## 참고 자료

- [Cordova 공식 문서](https://cordova.apache.org/docs/en/latest/)
- [cordova-plugin-camera](https://github.com/apache/cordova-plugin-camera)
- [cordova-plugin-ble-central](https://github.com/don/cordova-plugin-ble-central)
- [Android Developer Guide](https://developer.android.com/)
