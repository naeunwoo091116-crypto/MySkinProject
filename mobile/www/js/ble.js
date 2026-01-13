// Cordova BLE 플러그인 래퍼
class CordovaBLE {
    constructor() {
        this.isReady = false;
        this.connectedDevice = null;
        this.checkReady();
    }

    checkReady() {
        if (typeof ble !== 'undefined') {
            this.isReady = true;
            console.log('✅ Cordova BLE 플러그인 준비됨');
        } else {
            console.log('⏳ Cordova BLE 플러그인 대기 중...');
            setTimeout(() => this.checkReady(), 100);
        }
    }

    // BLE 스캔 시작
    scan(timeoutSeconds = 10) {
        return new Promise((resolve, reject) => {
            if (!this.isReady) {
                reject(new Error('BLE 플러그인이 준비되지 않았습니다'));
                return;
            }

            console.log('🔍 BLE 디바이스 스캔 시작...');
            const devices = [];

            ble.startScan(
                [],  // 모든 디바이스 스캔
                (device) => {
                    console.log('발견된 디바이스:', device.name || device.id);

                    // Seeed Xiao BLE 디바이스 필터링
                    if (device.name && device.name.includes('Xiao')) {
                        devices.push(device);
                    }
                },
                (error) => {
                    console.error('스캔 오류:', error);
                    reject(error);
                }
            );

            // 타임아웃 후 스캔 중지
            setTimeout(() => {
                ble.stopScan(
                    () => {
                        console.log(`✅ 스캔 완료: ${devices.length}개 디바이스 발견`);
                        resolve(devices);
                    },
                    (error) => {
                        console.error('스캔 중지 오류:', error);
                        reject(error);
                    }
                );
            }, timeoutSeconds * 1000);
        });
    }

    // 디바이스 연결
    connect(deviceId) {
        return new Promise((resolve, reject) => {
            if (!this.isReady) {
                reject(new Error('BLE 플러그인이 준비되지 않았습니다'));
                return;
            }

            console.log('🔗 디바이스 연결 시도:', deviceId);

            ble.connect(
                deviceId,
                (device) => {
                    console.log('✅ 디바이스 연결 성공:', device.name || device.id);
                    this.connectedDevice = device;
                    resolve(device);
                },
                (error) => {
                    console.error('❌ 연결 실패:', error);
                    this.connectedDevice = null;
                    reject(error);
                }
            );
        });
    }

    // 디바이스 연결 해제
    disconnect() {
        return new Promise((resolve, reject) => {
            if (!this.connectedDevice) {
                resolve();
                return;
            }

            const deviceId = this.connectedDevice.id;
            console.log('🔌 디바이스 연결 해제:', deviceId);

            ble.disconnect(
                deviceId,
                () => {
                    console.log('✅ 연결 해제 완료');
                    this.connectedDevice = null;
                    resolve();
                },
                (error) => {
                    console.error('❌ 연결 해제 실패:', error);
                    reject(error);
                }
            );
        });
    }

    // LED 모드 실행 명령 전송
    sendLEDCommand(mode, duration) {
        return new Promise((resolve, reject) => {
            if (!this.connectedDevice) {
                reject(new Error('연결된 디바이스가 없습니다'));
                return;
            }

            // 명령 형식: START:{MODE}:{DURATION} 또는 STOP
            let command;
            if (mode === 'STOP') {
                command = 'STOP';
            } else {
                command = `START:${mode.toUpperCase()}:${duration}`;
            }
            console.log('📤 명령 전송:', command);

            // 문자열을 ArrayBuffer로 변환
            const data = new TextEncoder().encode(command);

            ble.write(
                this.connectedDevice.id,
                APP_CONFIG.BLE.SERVICE_UUID,
                APP_CONFIG.BLE.CHARACTERISTIC_UUID,
                data.buffer,
                () => {
                    console.log('✅ 명령 전송 성공');
                    resolve();
                },
                (error) => {
                    console.error('❌ 명령 전송 실패:', error);
                    reject(error);
                }
            );
        });
    }

    // 연결 상태 확인
    isConnected() {
        return this.connectedDevice !== null;
    }

    // 연결된 디바이스 정보 반환
    getConnectedDevice() {
        return this.connectedDevice;
    }
}

// 전역 BLE 인스턴스
let cordovaBLE = null;

document.addEventListener('deviceready', function() {
    cordovaBLE = new CordovaBLE();
}, false);
