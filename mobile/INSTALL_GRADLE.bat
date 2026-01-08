@echo off
echo ==========================================
echo Gradle 자동 설치 스크립트
echo ==========================================
echo.

echo [1/3] Chocolatey 설치 확인 중...
where choco >nul 2>&1
if %errorlevel% neq 0 (
    echo Chocolatey가 설치되어 있지 않습니다.
    echo.
    echo 수동 설치 방법:
    echo 1. PowerShell을 관리자 권한으로 실행
    echo 2. 다음 명령어 실행:
    echo    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    echo 3. 이 스크립트를 다시 실행
    pause
    exit /b 1
)

echo [2/3] Gradle 설치 중...
choco install gradle -y

echo [3/3] Gradle 설치 확인...
gradle --version

echo.
echo ==========================================
echo 설치 완료!
echo ==========================================
echo.
echo 다음 명령어로 APK 빌드하세요:
echo   cordova build android
echo.
pause
