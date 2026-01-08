# Gradle 자동 다운로드 및 설치 스크립트
# PowerShell에서 실행하세요

Write-Host "========================================" -ForegroundColor Green
Write-Host "Gradle 자동 다운로드 및 설치" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 설정
$gradleVersion = "8.5"
$gradleUrl = "https://services.gradle.org/distributions/gradle-$gradleVersion-bin.zip"
$downloadPath = "$env:TEMP\gradle-$gradleVersion-bin.zip"
$installPath = "C:\Gradle"
$gradleHome = "$installPath\gradle-$gradleVersion"

# 1. Gradle 다운로드
Write-Host "[1/5] Gradle $gradleVersion 다운로드 중..." -ForegroundColor Yellow
Write-Host "URL: $gradleUrl"
Write-Host "다운로드 경로: $downloadPath"

try {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $gradleUrl -OutFile $downloadPath
    Write-Host "다운로드 완료!" -ForegroundColor Green
} catch {
    Write-Host "다운로드 실패: $_" -ForegroundColor Red
    Write-Host "수동 다운로드: $gradleUrl" -ForegroundColor Yellow
    exit 1
}

# 2. 설치 디렉토리 생성
Write-Host ""
Write-Host "[2/5] 설치 디렉토리 생성 중..." -ForegroundColor Yellow
if (-not (Test-Path $installPath)) {
    New-Item -ItemType Directory -Path $installPath -Force | Out-Null
    Write-Host "생성 완료: $installPath" -ForegroundColor Green
} else {
    Write-Host "디렉토리 이미 존재: $installPath" -ForegroundColor Green
}

# 3. 압축 해제
Write-Host ""
Write-Host "[3/5] 압축 해제 중..." -ForegroundColor Yellow
Write-Host "대상 경로: $gradleHome"

try {
    if (Test-Path $gradleHome) {
        Write-Host "기존 설치본 제거 중..." -ForegroundColor Yellow
        Remove-Item -Path $gradleHome -Recurse -Force
    }

    Expand-Archive -Path $downloadPath -DestinationPath $installPath -Force
    Write-Host "압축 해제 완료!" -ForegroundColor Green
} catch {
    Write-Host "압축 해제 실패: $_" -ForegroundColor Red
    exit 1
}

# 4. 환경변수 설정
Write-Host ""
Write-Host "[4/5] 환경변수 설정 중..." -ForegroundColor Yellow

# GRADLE_HOME 설정
[System.Environment]::SetEnvironmentVariable("GRADLE_HOME", $gradleHome, [System.EnvironmentVariableTarget]::Machine)
Write-Host "GRADLE_HOME = $gradleHome" -ForegroundColor Green

# PATH에 추가
$currentPath = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine)
$gradleBin = "$gradleHome\bin"

if ($currentPath -notlike "*$gradleBin*") {
    [System.Environment]::SetEnvironmentVariable("Path", "$currentPath;$gradleBin", [System.EnvironmentVariableTarget]::Machine)
    Write-Host "PATH에 추가됨: $gradleBin" -ForegroundColor Green
} else {
    Write-Host "PATH에 이미 존재함" -ForegroundColor Green
}

# 5. 임시 파일 정리
Write-Host ""
Write-Host "[5/5] 임시 파일 정리 중..." -ForegroundColor Yellow
Remove-Item -Path $downloadPath -Force
Write-Host "정리 완료!" -ForegroundColor Green

# 완료
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "설치 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Cyan
Write-Host "1. 이 PowerShell 창을 닫고 새 터미널을 여세요" -ForegroundColor Yellow
Write-Host "2. 설치 확인: gradle --version" -ForegroundColor Yellow
Write-Host "3. APK 빌드: cd mobile && cordova build android" -ForegroundColor Yellow
Write-Host ""
Write-Host "설치 경로: $gradleHome" -ForegroundColor Gray

# 현재 세션에서도 PATH 업데이트
$env:Path = "$env:Path;$gradleBin"
$env:GRADLE_HOME = $gradleHome

Write-Host ""
Write-Host "현재 세션에서도 Gradle이 활성화되었습니다." -ForegroundColor Green
Write-Host "확인: " -NoNewline
gradle --version

Read-Host -Prompt "엔터를 눌러 종료하세요"
