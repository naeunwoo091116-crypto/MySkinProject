# Android Studio 없이 APK 빌드하기

## 방법 1: Java JDK만 설치 (권장)

### 1단계: Java JDK 설치

1. **Temurin JDK 11 다운로드**
   - 링크: https://adoptium.net/temurin/releases/?version=11
   - Windows x64용 MSI 파일 다운로드
   - 설치 시 **"Set JAVA_HOME"** 체크박스 필수!

2. **설치 확인**
```powershell
java -version
javac -version
```

출력 예시:
```
openjdk version "11.0.xx"
javac 11.0.xx
```

### 2단계: Android SDK 간편 설치 (Command Line Tools)

#### 옵션 A: Chocolatey 사용 (추천)

```powershell
# PowerShell 관리자 권한으로 실행

# Chocolatey 설치 (없는 경우)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Android SDK 설치
choco install android-sdk -y

# 환경 변수 자동 설정됨
```

#### 옵션 B: 수동 설치

1. **SDK Command Line Tools 다운로드**
   - https://developer.android.com/studio#command-tools
   - "Command line tools only" 섹션에서 Windows용 다운로드

2. **압축 해제**
```
C:\Android\cmdline-tools\
```

3. **환경 변수 설정**
```powershell
# PowerShell 관리자 권한
setx ANDROID_HOME "C:\Android" /M
setx PATH "%PATH%;%ANDROID_HOME%\cmdline-tools\bin;%ANDROID_HOME%\platform-tools" /M
```

4. **재부팅 후 SDK 구성 요소 설치**
```bash
sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"
```

### 3단계: Gradle 자동 다운로드 설정

Cordova가 자동으로 Gradle을 다운로드하도록 설정:

```bash
cd C:\Users\naeun\Downloads\skin_care\MySkinProject\mobile
cordova build android
```

첫 빌드 시 Gradle Wrapper를 자동으로 다운로드합니다 (시간 소요: 5-10분)

### 4단계: APK 빌드

```bash
cd C:\Users\naeun\Downloads\skin_care\MySkinProject\mobile
cordova build android --verbose
```

**출력 위치:**
```
platforms\android\app\build\outputs\apk\debug\app-debug.apk
```

---

## 방법 2: 온라인 빌드 서비스 (가장 쉬움)

별도 설치 없이 온라인에서 APK 생성!

### PhoneGap Build (Adobe)
- 링크: https://build.phonegap.com/
- 무료 플랜: 1개 앱
- GitHub 연동 가능

**단계:**
1. GitHub에 mobile 폴더 푸시
2. PhoneGap Build 계정 생성
3. 저장소 연결
4. "Build" 클릭
5. APK 다운로드

---

## 방법 3: 웹앱으로 배포 (설치 불필요)

PWA(Progressive Web App)로 변환하면 별도 설치 없이 사용 가능!

### 장점:
- APK 빌드 불필요
- 안드로이드 + iOS + PC 모두 지원
- 자동 업데이트

### 단계:

1. **manifest.json 생성**
```json
{
  "name": "MySkin",
  "short_name": "MySkin",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#10B981",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

2. **Service Worker 추가**
```javascript
// sw.js
self.addEventListener('install', (e) => {
  console.log('Service Worker 설치됨');
});
```

3. **index.html에 추가**
```html
<link rel="manifest" href="/manifest.json">
<script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js');
  }
</script>
```

4. **사용 방법**
- Chrome에서 웹사이트 접속
- 설정 메뉴 > "홈 화면에 추가"
- 앱처럼 사용!

---

## 방법 4: React Native 변환 (고급)

완전한 네이티브 앱을 원한다면 React Native로 재작성.

---

## 추천 순서

### 시간이 별로 없다면:
**방법 2 (온라인 빌드)** → 가장 빠름

### 로컬에서 관리하고 싶다면:
**방법 1 (Java JDK + Gradle)** → 한 번만 설정하면 계속 사용

### APK가 필요 없다면:
**방법 3 (PWA)** → 가장 유연함

---

## 현재 상태 체크

이미 완료된 것:
- ✅ Cordova 설치
- ✅ Android 플랫폼 추가
- ✅ 플러그인 설치
- ✅ HTML 변환

필요한 것:
- ⚠️ Java JDK 설치
- ⚠️ Android SDK (또는 온라인 빌드)

---

## 문제 해결

### "JAVA_HOME not found"
```powershell
# 확인
echo %JAVA_HOME%

# 수동 설정
setx JAVA_HOME "C:\Program Files\Eclipse Adoptium\jdk-11.x.x-hotspot"
```

### "Gradle not found"
첫 빌드 시 자동 다운로드됩니다. 인터넷 연결 확인!

### "License not accepted"
```bash
sdkmanager --licenses
# 모든 라이선스에 "y" 입력
```
