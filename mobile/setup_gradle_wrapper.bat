@echo off
echo ==========================================
echo Gradle Wrapper 자동 생성
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/2] Android 프로젝트 폴더로 이동...
cd platforms\android

echo [2/2] Gradle Wrapper 생성 중...
echo.
echo 다음 URL에서 gradle-wrapper.jar를 다운로드합니다:
echo https://github.com/gradle/gradle/raw/master/gradle/wrapper/gradle-wrapper.jar
echo.

mkdir gradle\wrapper 2>nul

powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/gradle/gradle/master/gradle/wrapper/gradle-wrapper.jar' -OutFile 'gradle\wrapper\gradle-wrapper.jar'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/gradle/gradle/master/gradle/wrapper/gradle-wrapper.properties' -OutFile 'gradle\wrapper\gradle-wrapper.properties'"

echo.
echo ==========================================
echo Gradle Wrapper 생성 완료!
echo ==========================================
echo.
echo 다음 명령어로 빌드하세요:
echo   cd ..\..
echo   cordova build android
echo.
pause
