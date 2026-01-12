// Cordova 카메라 플러그인 래퍼
class CordovaCamera {
    constructor() {
        this.isReady = false;
        this.checkReady();
    }

    checkReady() {
        if (typeof Camera !== 'undefined') {
            this.isReady = true;
            console.log('✅ Cordova Camera 플러그인 준비됨');
        } else {
            console.log('⏳ Cordova Camera 플러그인 대기 중...');
            setTimeout(() => this.checkReady(), 100);
        }
    }

    // 카메라로 사진 촬영
    takePicture() {
        return new Promise((resolve, reject) => {
            if (!this.isReady) {
                reject(new Error('카메라 플러그인이 준비되지 않았습니다'));
                return;
            }

            navigator.camera.getPicture(
                (imageData) => {
                    // imageData는 이미 Base64 문자열 (접두사 없음)
                    // destinationType이 0 (DATA_URL)이면 접두사 추가
                    if (imageData.startsWith('data:')) {
                        // 이미 data URL 형식
                        resolve(imageData);
                    } else {
                        // Base64 문자열만 있으면 접두사 추가
                        resolve('data:image/jpeg;base64,' + imageData);
                    }
                },
                (error) => {
                    console.error('카메라 오류:', error);
                    reject(new Error(error));
                },
                APP_CONFIG.CAMERA
            );
        });
    }

    // 갤러리에서 사진 선택
    selectFromGallery() {
        return new Promise((resolve, reject) => {
            if (!this.isReady) {
                reject(new Error('카메라 플러그인이 준비되지 않았습니다'));
                return;
            }

            const options = {
                ...APP_CONFIG.CAMERA,
                sourceType: Camera.PictureSourceType.PHOTOLIBRARY
            };

            navigator.camera.getPicture(
                (imageData) => {
                    resolve('data:image/jpeg;base64,' + imageData);
                },
                (error) => {
                    console.error('갤러리 오류:', error);
                    reject(new Error(error));
                },
                options
            );
        });
    }

    // Base64를 Blob으로 변환
    dataURLtoBlob(dataURL) {
        try {
            // dataURL 형식 검증
            if (!dataURL || typeof dataURL !== 'string') {
                throw new Error('Invalid dataURL');
            }

            const arr = dataURL.split(',');
            if (arr.length !== 2) {
                throw new Error('Invalid dataURL format');
            }

            const mimeMatch = arr[0].match(/:(.*?);/);
            if (!mimeMatch) {
                throw new Error('Cannot extract MIME type');
            }

            const mime = mimeMatch[1];
            const bstr = atob(arr[1]); // Base64 디코딩
            let n = bstr.length;
            const u8arr = new Uint8Array(n);

            while (n--) {
                u8arr[n] = bstr.charCodeAt(n);
            }

            return new Blob([u8arr], { type: mime });
        } catch (error) {
            console.error('dataURLtoBlob 오류:', error);
            throw error;
        }
    }

    // 이미지 업로드 (Flask API로 전송)
    async uploadImage(imageDataURL, userId) {
        try {
            // Base64를 Blob으로 변환
            const blob = this.dataURLtoBlob(imageDataURL);

            // FormData 생성
            const formData = new FormData();
            formData.append('file', blob, 'photo.jpg');
            formData.append('user_id', userId || 'default_user');

            // Flask API로 전송
            const response = await fetch(API.analysisFace(), {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`서버 오류: ${response.status} - ${errorText}`);
            }

            const result = await response.json();
            console.log('✅ 분석 완료:', result);
            return result;

        } catch (error) {
            console.error('❌ 이미지 업로드 실패:', error);
            throw error;
        }
    }
}

// 전역 카메라 인스턴스
let cordovaCamera = null;

document.addEventListener('deviceready', function() {
    cordovaCamera = new CordovaCamera();
}, false);
