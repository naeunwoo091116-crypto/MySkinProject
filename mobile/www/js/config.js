// Cordova 앱 설정
const APP_CONFIG = {
    // Flask 백엔드 서버 주소 (로컬 테스트용 - 실제 배포 시 변경 필요)
    // 안드로이드 에뮬레이터: 10.0.2.2:5001
    // 실제 기기: WiFi IP 주소 (예: 192.168.0.10:5001)
    // 배포용: 실제 서버 URL
    API_BASE_URL: 'http://192.168.219.186:5001',  // 실제 PC IP

    // BLE 디바이스 설정
    BLE: {
        SERVICE_UUID: '0000ffe0-0000-1000-8000-00805f9b34fb',
        CHARACTERISTIC_UUID: '0000ffe1-0000-1000-8000-00805f9b34fb',
        DEVICE_NAME: 'Seeed Xiao BLE'
    },

    // 카메라 설정 (Camera 객체는 deviceready 이후에 사용 가능)
    CAMERA: {
        quality: 80,
        destinationType: 0,  // Camera.DestinationType.DATA_URL
        sourceType: 1,       // Camera.PictureSourceType.CAMERA
        encodingType: 0,     // Camera.EncodingType.JPEG
        mediaType: 0,        // Camera.MediaType.PICTURE
        allowEdit: false,
        correctOrientation: true,
        targetWidth: 1024,
        targetHeight: 1024
    }
};

// API 엔드포인트 헬퍼
const API = {
    analysisFace: () => `${APP_CONFIG.API_BASE_URL}/api/v1/analysis/face`,
    saveHistory: () => `${APP_CONFIG.API_BASE_URL}/api/v1/history`,
    getHistory: (userId) => `${APP_CONFIG.API_BASE_URL}/api/v1/history/${userId}`,
    getStats: (userId) => `${APP_CONFIG.API_BASE_URL}/api/v1/stats/${userId}`,
    saveProfile: () => `${APP_CONFIG.API_BASE_URL}/api/v1/user/profile`,
    getProfile: (userId) => `${APP_CONFIG.API_BASE_URL}/api/v1/user/profile/${userId}`,
    getUsers: () => `${APP_CONFIG.API_BASE_URL}/api/v1/users`,
    deleteUser: (userId) => `${APP_CONFIG.API_BASE_URL}/api/v1/user/${userId}`,
    getDeviceConfig: () => `${APP_CONFIG.API_BASE_URL}/api/v1/device/config`,
    getDeviceModes: () => `${APP_CONFIG.API_BASE_URL}/api/v1/device/modes`
};

// 서버 연결 테스트
function testServerConnection() {
    return fetch(API.getDeviceModes())
        .then(response => {
            if (!response.ok) throw new Error('서버 응답 오류');
            return response.json();
        })
        .then(() => {
            console.log('✅ 서버 연결 성공:', APP_CONFIG.API_BASE_URL);
            return true;
        })
        .catch(error => {
            console.error('❌ 서버 연결 실패:', error);
            // showToast가 정의되어 있으면 호출
            if (typeof showToast === 'function') {
                showToast('서버에 연결할 수 없습니다. 네트워크를 확인해주세요.', 'error');
            }
            return false;
        });
}

// Cordova deviceready 이벤트 핸들러
document.addEventListener('deviceready', function() {
    console.log('✅ Cordova 초기화 완료');
    console.log('디바이스 정보:', device.platform, device.version);

    // 서버 연결 테스트
    testServerConnection();

    // 뒤로가기 버튼 처리 (Android)
    document.addEventListener('backbutton', function(e) {
        e.preventDefault();

        // 현재 활성 탭 확인
        const activeTab = document.querySelector('.tab-content.active');
        if (activeTab && activeTab.id === 'home-tab') {
            // 홈 화면이면 앱 종료 확인
            if (confirm('앱을 종료하시겠습니까?')) {
                navigator.app.exitApp();
            }
        } else {
            // 다른 화면이면 홈으로 이동
            switchTab('home');
        }
    }, false);

    // 일시정지/재개 이벤트
    document.addEventListener('pause', function() {
        console.log('앱 일시정지');
    }, false);

    document.addEventListener('resume', function() {
        console.log('앱 재개');
        testServerConnection();
    }, false);
}, false);
