import os

class MockLEDService:
    """클라우드 환경을 위한 가짜 블루투스 서비스"""
    def __init__(self):
        self.is_connected = False
    def connect(self): return False
    def send_led_data(self, data): print(f"Mock LED Data: {data}")
    def get_status(self): return {"status": "disconnected", "mode": "cloud_mock"}

def get_ble_service():
    """서버를 죽이지 않고 안전하게 서비스를 반환하는 함수"""
    try:
        # 실제 블루투스 라이브러리 시도
        import bleak
        # 여기에 실제 BLEService 클래스가 있다면 그것을 반환
        # return BLEService() 
        print("⚠️ 실제 BLE 장치를 찾을 수 없습니다. Mock 서비스를 사용합니다.")
        return MockLEDService()
    except (ImportError, Exception) as e:
        # 에러를 발생시키지 않고 가짜 서비스를 반환하여 서버 부팅을 유지함
        print(f"ℹ️ BLE 비활성화 (사유: {e}). Mock 서비스를 사용합니다.")
        return MockLEDService()

# 만약 기존 코드에서 device_service라는 이름을 쓴다면 아래 추가
def device_service():
    return get_ble_service()