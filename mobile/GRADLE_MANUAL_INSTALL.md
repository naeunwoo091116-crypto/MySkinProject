# Gradle 수동 설치 가이드

## 1단계: Gradle 다운로드

1. **다운로드 페이지 접속**
   ```
   https://gradle.org/releases/
   ```

2. **최신 버전 다운로드**
   - "Binary-only" 클릭
   - 파일: `gradle-8.5-bin.zip` (약 100MB)
   - 다운로드 폴더에 저장

## 2단계: 압축 해제

1. **다운로드한 zip 파일 우클릭** → "압축 풀기"

2. **C 드라이브로 이동**
   ```
   압축 푼 폴더를 다음 경로로 이동:
   C:\Gradle\gradle-8.5\
   ```

   최종 구조:
   ```
   C:\Gradle\gradle-8.5\
   ├── bin\
   ├── lib\
   ├── LICENSE
   └── ...
   ```

## 3단계: 환경변수 설정

### 방법 A: PowerShell 스크립트 (자동)

PowerShell을 **관리자 권한**으로 열고 다음 실행:

```powershell
# Gradle 경로 설정 (본인의 버전에 맞게 수정)
$gradleHome = "C:\Gradle\gradle-8.5"

# GRADLE_HOME 환경변수 설정
[System.Environment]::SetEnvironmentVariable("GRADLE_HOME", $gradleHome, [System.EnvironmentVariableTarget]::Machine)

# PATH에 추가
$currentPath = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine)
if ($currentPath -notlike "*$gradleHome\bin*") {
    [System.Environment]::SetEnvironmentVariable("Path", "$currentPath;$gradleHome\bin", [System.EnvironmentVariableTarget]::Machine)
}

Write-Host "Gradle 환경변수 설정 완료!"
Write-Host "새 터미널을 열어서 'gradle --version'으로 확인하세요."
```

### 방법 B: GUI로 수동 설정

1. **시스템 환경 변수 열기**
   - Windows 검색 → "환경 변수" → "시스템 환경 변수 편집"

2. **GRADLE_HOME 추가**
   - "시스템 변수" → "새로 만들기"
   - 변수 이름: `GRADLE_HOME`
   - 변수 값: `C:\Gradle\gradle-8.5`
   - "확인"

3. **Path에 추가**
   - "시스템 변수"에서 `Path` 선택 → "편집"
   - "새로 만들기"
   - `%GRADLE_HOME%\bin` 입력
   - "확인"

4. **모든 창 닫기**

## 4단계: 설치 확인

1. **모든 터미널 창 닫기**

2. **새 PowerShell 또는 CMD 열기**

3. **확인 명령어**

```bash
gradle --version
```

**정상 출력:**
```
------------------------------------------------------------
Gradle 8.5
------------------------------------------------------------

Build time:   2023-11-29
Revision:     ...

Kotlin:       1.9.20
Groovy:       3.0.17
Ant:          Apache Ant(TM) version 1.10.13
JVM:          25.0.1 (Oracle Corporation)
OS:           Windows 10
```

## 5단계: APK 빌드

```bash
cd C:\Users\naeun\Downloads\skin_care\MySkinProject\mobile
cordova build android
```

**빌드 성공 시 출력:**
```
BUILD SUCCESSFUL in 1m 23s
Built the following apk(s):
  platforms\android\app\build\outputs\apk\debug\app-debug.apk
```

## APK 위치

```
C:\Users\naeun\Downloads\skin_care\MySkinProject\mobile\platforms\android\app\build\outputs\apk\debug\app-debug.apk
```

이 파일을 휴대폰으로 전송해서 설치하면 됩니다!

---

## 문제 해결

### ❌ "gradle: command not found"

**원인:** 환경변수가 적용되지 않음

**해결:**
1. 모든 터미널 완전 종료
2. 새 터미널 열기
3. 또는 컴퓨터 재부팅

### ❌ "JAVA_HOME is not set"

**원인:** Java 환경변수 미설정

**해결:**
- 이전에 설정한 JAVA_HOME 확인:
  ```powershell
  echo $env:JAVA_HOME
  ```
- 출력 없으면 JAVA_SETUP.md 참고

### ❌ 빌드 시 "SDK location not found"

**해결:**
```bash
# ANDROID_HOME 설정
setx ANDROID_HOME "C:\Users\naeun\AppData\Local\Android\Sdk" /M
```

---

## 직접 다운로드 링크

**Gradle 8.5 (추천):**
```
https://services.gradle.org/distributions/gradle-8.5-bin.zip
```

**Gradle 7.6 (안정 버전):**
```
https://services.gradle.org/distributions/gradle-7.6-bin.zip
```
