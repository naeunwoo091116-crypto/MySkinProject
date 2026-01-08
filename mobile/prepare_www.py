#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask templates/index.html을 Cordova www/index.html로 변환하는 스크립트
"""

import os
import sys
import re
import shutil
from pathlib import Path

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def prepare_cordova_www():
    """Cordova www 폴더 준비"""

    # 경로 설정
    project_root = Path(__file__).parent.parent
    template_file = project_root / 'templates' / 'index.html'
    www_dir = Path(__file__).parent / 'www'
    output_file = www_dir / 'index.html'

    print(f"[INFO] 프로젝트 루트: {project_root}")
    print(f"[INFO] 원본 파일: {template_file}")
    print(f"[INFO] 출력 디렉토리: {www_dir}")

    # www 디렉토리 생성
    www_dir.mkdir(exist_ok=True)
    (www_dir / 'js').mkdir(exist_ok=True)
    (www_dir / 'css').mkdir(exist_ok=True)
    (www_dir / 'img').mkdir(exist_ok=True)

    # HTML 파일 읽기
    if not template_file.exists():
        print(f"[ERROR] 원본 파일을 찾을 수 없습니다: {template_file}")
        return False

    with open(template_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Cordova 설정 추가
    cordova_scripts = '''
    <!-- Cordova Scripts -->
    <script type="text/javascript" src="cordova.js"></script>
    <script type="text/javascript" src="js/config.js"></script>
    <script type="text/javascript" src="js/camera.js"></script>
    <script type="text/javascript" src="js/ble.js"></script>
'''

    # </head> 태그 앞에 Cordova 스크립트 삽입
    html_content = html_content.replace('</head>', cordova_scripts + '\n</head>')

    # CSP(Content Security Policy) 메타 태그 추가
    csp_meta = '''
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' data: gap: https://ssl.gstatic.com 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; media-src *; img-src 'self' data: content: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com;">
'''
    html_content = html_content.replace('<meta name="viewport"', csp_meta + '\n    <meta name="viewport"')

    # API 호출 부분을 config.js의 API 헬퍼로 변경하는 주석 추가
    api_comment = '''
    /*
     * Cordova용 API 호출 수정 필요:
     * - fetch('/api/v1/...') → fetch(API.analysisFace()) 등으로 변경
     * - 카메라: cordovaCamera.takePicture() 사용
     * - BLE: cordovaBLE.scan(), cordovaBLE.connect() 사용
     */
    '''

    # <script> 태그 내부에 주석 추가
    html_content = re.sub(
        r'(<script>\s*)',
        r'\1' + api_comment,
        html_content,
        count=1
    )

    # HTML 파일 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[SUCCESS] {output_file} 생성 완료")

    # static 폴더가 있으면 복사
    static_dir = project_root / 'static'
    if static_dir.exists():
        print(f"[INFO] static 폴더 복사 중...")
        for item in static_dir.rglob('*'):
            if item.is_file():
                rel_path = item.relative_to(static_dir)
                dest = www_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
                print(f"  [OK] {rel_path}")

    print("\n[SUCCESS] Cordova www 폴더 준비 완료!")
    print(f"\n다음 단계:")
    print(f"1. cd mobile")
    print(f"2. npm install")
    print(f"3. cordova platform add android")
    print(f"4. npm run install:plugins")
    print(f"5. www/index.html에서 API 호출 부분 수정 (주석 참고)")
    print(f"6. cordova build android")

    return True

if __name__ == '__main__':
    prepare_cordova_www()
