"""
BLE 디바이스 통신 서비스 (Mock 버전)
블루투스 어댑터가 없는 환경에서 개발/테스트용
"""
import asyncio
from typing import Optional, Dict, Any
from core.logger import setup_logger
from core.constants import DEVICE_CONFIG

logger = setup_logger(__name__)


class BLEDeviceServiceMock:
    """BLE 디바이스 통신 서비스 (Mock)"""

    def __init__(self):
        self.device_name = DEVICE_CONFIG["device_name"]
        self.service_uuid = DEVICE_CONFIG["ble_service_uuid"]
        self.device_address: Optional[str] = "MOCK:XX:XX:XX:XX:XX"
        self._connected = False
        self._therapy_active = False
        self._therapy_mode = None
        self._therapy_duration = 0
        self._therapy_start_time = None

        logger.warning("⚠️ Mock BLE Service 사용 중 - 실제 하드웨어 연결 없음")

    async def scan_devices(self, timeout: int = 10) -> list:
        """
        BLE 디바이스 스캔 (Mock)
        """
        logger.info(f"[MOCK] BLE 디바이스 스캔 시뮬레이션 ({timeout}초)")

        # 짧은 지연으로 스캔 시뮬레이션
        await asyncio.sleep(1)

        mock_devices = [
            {
                "name": "MySkin_LED_Mask",
                "address": "MOCK:E8:31:CD:12:34:56",
                "rssi": -45
            },
            {
                "name": "Other_Device",
                "address": "MOCK:AA:BB:CC:DD:EE:FF",
                "rssi": -67
            }
        ]

        logger.info(f"[MOCK] {len(mock_devices)}개의 디바이스 발견 (시뮬레이션)")
        self.device_address = mock_devices[0]["address"]
        return mock_devices

    async def connect(self, address: Optional[str] = None) -> bool:
        """
        BLE 디바이스 연결 (Mock)
        """
        if self._connected:
            logger.info("[MOCK] 이미 연결된 디바이스가 있습니다")
            return True

        try:
            # 주소가 없으면 스캔
            if address is None:
                if self.device_address is None:
                    await self.scan_devices()
                address = self.device_address

            if address is None:
                logger.error("[MOCK] 연결할 디바이스를 찾을 수 없습니다")
                return False

            logger.info(f"[MOCK] 디바이스 연결 시뮬레이션: {address}")

            # 연결 시뮬레이션
            await asyncio.sleep(0.5)

            self._connected = True
            self.device_address = address
            logger.info(f"[MOCK] 디바이스 연결 성공: {address}")
            return True

        except Exception as e:
            logger.error(f"[MOCK] BLE 연결 오류: {e}")
            return False

    async def disconnect(self):
        """BLE 디바이스 연결 해제 (Mock)"""
        if self._connected:
            logger.info("[MOCK] 디바이스 연결 해제 시뮬레이션")
            await asyncio.sleep(0.3)
            self._connected = False
            self._therapy_active = False
            logger.info("[MOCK] 디바이스 연결 해제 완료")

    async def send_command(self, command: str) -> str:
        """
        BLE 디바이스에 명령 전송 (Mock)
        """
        if not self._connected:
            raise ConnectionError("[MOCK] 디바이스가 연결되지 않았습니다")

        logger.info(f"[MOCK] 명령 전송: {command}")
        await asyncio.sleep(0.3)

        # 명령에 따른 Mock 응답
        if command.startswith("START:"):
            return "OK:STARTED:RED:20"
        elif command == "STOP":
            return "OK:STOPPED"
        elif command == "STATUS":
            if self._therapy_active:
                return "ACTIVE:RED:1200"
            return "IDLE"
        else:
            return "OK"

    async def start_therapy(self, mode: str, duration: int) -> Dict[str, Any]:
        """
        LED 테라피 시작 (Mock)
        """
        command = f"START:{mode.upper()}:{duration}"

        try:
            logger.info(f"[MOCK] 테라피 시작 시뮬레이션: {mode}, {duration}분")
            await asyncio.sleep(0.5)

            self._therapy_active = True
            self._therapy_mode = mode.upper()
            self._therapy_duration = duration
            self._therapy_start_time = asyncio.get_event_loop().time()

            return {
                "success": True,
                "mode": mode.upper(),
                "duration": duration,
                "message": "[MOCK] 테라피가 시작되었습니다 (시뮬레이션)"
            }

        except Exception as e:
            logger.error(f"[MOCK] 테라피 시작 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "[MOCK] 테라피 시작 중 오류 발생"
            }

    async def stop_therapy(self) -> Dict[str, Any]:
        """
        LED 테라피 중지 (Mock)
        """
        try:
            logger.info("[MOCK] 테라피 중지 시뮬레이션")
            await asyncio.sleep(0.3)

            self._therapy_active = False
            self._therapy_mode = None

            return {
                "success": True,
                "message": "[MOCK] 테라피가 중지되었습니다 (시뮬레이션)"
            }

        except Exception as e:
            logger.error(f"[MOCK] 테라피 중지 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "[MOCK] 테라피 중지 중 오류 발생"
            }

    async def get_status(self) -> Dict[str, Any]:
        """
        디바이스 상태 조회 (Mock)
        """
        if not self._connected:
            return {
                "connected": False,
                "status": "disconnected",
                "message": "[MOCK] 연결되지 않음"
            }

        if self._therapy_active:
            # 남은 시간 계산 (시뮬레이션)
            elapsed = asyncio.get_event_loop().time() - self._therapy_start_time
            total_seconds = self._therapy_duration * 60
            remaining = max(0, int(total_seconds - elapsed))

            return {
                "connected": True,
                "status": "active",
                "mode": self._therapy_mode,
                "remaining_seconds": remaining,
                "message": "[MOCK] 테라피 진행 중 (시뮬레이션)"
            }
        else:
            return {
                "connected": True,
                "status": "idle",
                "message": "[MOCK] 대기 중"
            }

    def is_connected(self) -> bool:
        """연결 상태 확인 (Mock)"""
        return self._connected


# 싱글톤 인스턴스
_ble_service_mock_instance: Optional[BLEDeviceServiceMock] = None


def get_ble_service_mock() -> BLEDeviceServiceMock:
    """BLE 서비스 Mock 싱글톤 인스턴스 획득"""
    global _ble_service_mock_instance
    if _ble_service_mock_instance is None:
        _ble_service_mock_instance = BLEDeviceServiceMock()
    return _ble_service_mock_instance
