# Flask 서버 설정 가이드 (모바일 앱용)

APK로 빌드한 앱에서 AI 분석이 작동하려면 Flask 서버를 설정해야 합니다.

## 1단계: PC IP 주소 확인

### Windows
```cmd
ipconfig
```

출력 예시에서 **Wi-Fi의 IPv4 주소** 찾기:
```
무선 LAN 어댑터 Wi-Fi:
   IPv4 주소 . . . . . . . . : 192.168.0.10
```

## 2단계: Flask 서버 설정

`app.py` 파일 수정:

```python
if __name__ == '__main__':
    # 0.0.0.0으로 변경 (모든 네트워크 인터페이스에서 접근 가능)
    app.run(host='0.0.0.0', port=5001, debug=True)
```

## 3단계: 방화벽 허용

### Windows Defender 방화벽
1. Windows 검색 → "Windows Defender 방화벽"
2. "고급 설정" 클릭
3. "인바운드 규칙" → "새 규칙"
4. 포트 → TCP → 5001 → 허용
5. 규칙 이름: "Flask Server"

### 빠른 방법 (PowerShell 관리자 권한)
```powershell
New-NetFirewallRule -DisplayName "Flask Server" -Direction Inbound -LocalPort 5001 -Protocol TCP -Action Allow
```

## 4단계: config.js 수정

`mobile/www/js/config.js` 파일에서 IP 주소 변경:

```javascript
const APP_CONFIG = {
    // PC IP로 변경 (ipconfig에서 확인한 IP)
    API_BASE_URL: 'http://192.168.0.10:5001',  // ← 본인 IP로 수정

    BLE: {
        // ... 나머지 설정
    }
};
```

## 5단계: APK 재빌드

```bash
cd mobile
export JAVA_HOME="/c/Program Files/Java/jdk-17"
cordova build android
```

## 6단계: 테스트

### PC에서:
```bash
cd C:\Users\naeun\Downloads\skin_care\MySkinProject
venv1\Scripts\activate
python app.py
```

출력:
```
* Running on all addresses (0.0.0.0)
* Running on http://192.168.0.10:5001
```

### 휴대폰에서:
1. **PC와 같은 WiFi 연결**
2. 브라우저에서 `http://192.168.0.10:5001` 접속
3. 웹이 열리면 서버 연결 성공!
4. APK 설치 후 앱 실행

## 문제 해결

### "서버에 연결할 수 없습니다"
- [ ] PC와 휴대폰이 같은 WiFi에 연결되어 있는지 확인
- [ ] Flask 서버가 실행 중인지 확인
- [ ] 방화벽에서 5001 포트가 허용되어 있는지 확인
- [ ] `config.js`의 IP 주소가 올바른지 확인

### BLE 연결 안됨
- [ ] 앱 설정 → 권한 → 위치, 블루투스 허용
- [ ] Android 12 이상: "근처 기기" 권한 허용
- [ ] BLE 디바이스가 켜져 있는지 확인

### 아이콘 깨짐 (X 표시)
- [ ] 인터넷 연결 확인 (CDN에서 아이콘 로드)
- [ ] APK 재빌드 (CSP 설정 수정됨)

## 빠른 체크리스트

설정 전:
- [ ] PC IP 주소 확인 (ipconfig)
- [ ] app.py에서 host='0.0.0.0' 설정
- [ ] 방화벽 포트 5001 허용
- [ ] config.js에 PC IP 입력
- [ ] APK 재빌드

실행 시:
- [ ] PC와 휴대폰 같은 WiFi 연결
- [ ] Flask 서버 실행 중
- [ ] 앱에서 권한 모두 허용
