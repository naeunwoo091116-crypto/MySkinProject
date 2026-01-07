"""
BLE 디바이스 통신 서비스
Seeed Xiao BLE와의 블루투스 통신 관리
"""
import asyncio
from typing import Optional, Dict, Any
from core.logger import setup_logger
from core.constants import DEVICE_CONFIG

# bleak import 시도 - 실패하면 예외 발생하도록 유지
try:
    from bleak import BleakClient, BleakScanner
    BLEAK_AVAILABLE = True
except Exception as e:
    BLEAK_AVAILABLE = False
    BleakClient = None
    BleakScanner = None
    print(f"⚠️ bleak 라이브러리를 불러올 수 없습니다: {e}")

logger = setup_logger(__name__)


class BLEDeviceService:
    """BLE 디바이스 통신 서비스"""

    def __init__(self):
        if not BLEAK_AVAILABLE:
            raise ImportError("bleak 라이브러리를 사용할 수 없습니다. Mock 모드를 사용하세요.")

        self.device_name = DEVICE_CONFIG["device_name"]
        self.service_uuid = DEVICE_CONFIG["ble_service_uuid"]
        self.char_uuid = "0000ffe1-0000-1000-8000-00805f9b34fb"
        self.client: Optional[BleakClient] = None
        self.device_address: Optional[str] = None
        self._connection_lock = asyncio.Lock()

    async def scan_devices(self, timeout: int = 10) -> list:
        """
        BLE 디바이스 스캔

        Args:
            timeout: 스캔 타임아웃(초)

        Returns:
            발견된 디바이스 리스트
        """
        logger.info(f"BLE 디바이스 스캔 시작 (타임아웃: {timeout}초)")

        try:
            devices = await BleakScanner.discover(timeout=timeout)
            found_devices = []

            for device in devices:
                device_info = {
                    "name": device.name or "Unknown",
                    "address": device.address,
                    "rssi": device.rssi
                }
                found_devices.append(device_info)

                if device.name == self.device_name:
                    logger.info(f"MySkin 디바이스 발견: {device.address} (RSSI: {device.rssi})")
                    self.device_address = device.address

            logger.info(f"{len(found_devices)}개의 BLE 디바이스 발견")
            return found_devices

        except Exception as e:
            logger.error(f"BLE 스캔 실패: {e}")
            raise

    async def connect(self, address: Optional[str] = None) -> bool:
        """
        BLE 디바이스 연결

        Args:
            address: 디바이스 주소 (None이면 자동 스캔)

        Returns:
            연결 성공 여부
        """
        async with self._connection_lock:
            if self.client and self.client.is_connected:
                logger.info("이미 연결된 디바이스가 있습니다")
                return True

            try:
                # 주소가 없으면 스캔
                if address is None:
                    if self.device_address is None:
                        await self.scan_devices()
                    address = self.device_address

                if address is None:
                    logger.error("연결할 디바이스를 찾을 수 없습니다")
                    return False

                logger.info(f"디바이스 연결 시도: {address}")
                self.client = BleakClient(address)
                await self.client.connect()

                if self.client.is_connected:
                    logger.info(f"디바이스 연결 성공: {address}")

                    # 서비스 확인
                    services = await self.client.get_services()
                    logger.info(f"사용 가능한 서비스 수: {len(services.services)}")

                    return True
                else:
                    logger.error("디바이스 연결 실패")
                    return False

            except Exception as e:
                logger.error(f"BLE 연결 오류: {e}")
                self.client = None
                return False

    async def disconnect(self):
        """BLE 디바이스 연결 해제"""
        async with self._connection_lock:
            if self.client and self.client.is_connected:
                try:
                    await self.client.disconnect()
                    logger.info("디바이스 연결 해제 완료")
                except Exception as e:
                    logger.error(f"연결 해제 오류: {e}")
                finally:
                    self.client = None

    async def send_command(self, command: str) -> str:
        """
        BLE 디바이스에 명령 전송

        Args:
            command: 전송할 명령 문자열

        Returns:
            디바이스 응답
        """
        if not self.client or not self.client.is_connected:
            raise ConnectionError("디바이스가 연결되지 않았습니다")

        try:
            logger.info(f"명령 전송: {command}")

            # 명령 전송
            await self.client.write_gatt_char(
                self.char_uuid,
                command.encode('utf-8')
            )

            # 응답 대기 (짧은 지연)
            await asyncio.sleep(0.5)

            # 응답 읽기
            response = await self.client.read_gatt_char(self.char_uuid)
            response_str = response.decode('utf-8').strip()

            logger.info(f"디바이스 응답: {response_str}")
            return response_str

        except Exception as e:
            logger.error(f"명령 전송 오류: {e}")
            raise

    async def start_therapy(self, mode: str, duration: int) -> Dict[str, Any]:
        """
        LED 테라피 시작

        Args:
            mode: LED 모드 (red, blue, gold)
            duration: 지속 시간(분)

        Returns:
            응답 딕셔너리
        """
        command = f"START:{mode.upper()}:{duration}"

        try:
            response = await self.send_command(command)

            if response.startswith("OK:STARTED"):
                parts = response.split(':')
                return {
                    "success": True,
                    "mode": parts[2] if len(parts) > 2 else mode,
                    "duration": int(parts[3]) if len(parts) > 3 else duration,
                    "message": "테라피가 시작되었습니다"
                }
            elif response.startswith("ERROR"):
                error_type = response.split(':')[1] if ':' in response else "UNKNOWN"
                return {
                    "success": False,
                    "error": error_type,
                    "message": f"테라피 시작 실패: {error_type}"
                }
            else:
                return {
                    "success": False,
                    "error": "UNKNOWN_RESPONSE",
                    "message": f"알 수 없는 응답: {response}"
                }

        except Exception as e:
            logger.error(f"테라피 시작 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "테라피 시작 중 오류 발생"
            }

    async def stop_therapy(self) -> Dict[str, Any]:
        """
        LED 테라피 중지

        Returns:
            응답 딕셔너리
        """
        try:
            response = await self.send_command("STOP")

            if response.startswith("OK:STOPPED"):
                return {
                    "success": True,
                    "message": "테라피가 중지되었습니다"
                }
            else:
                return {
                    "success": False,
                    "message": f"중지 실패: {response}"
                }

        except Exception as e:
            logger.error(f"테라피 중지 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "테라피 중지 중 오류 발생"
            }

    async def get_status(self) -> Dict[str, Any]:
        """
        디바이스 상태 조회

        Returns:
            상태 딕셔너리
        """
        if not self.client or not self.client.is_connected:
            return {
                "connected": False,
                "status": "disconnected"
            }

        try:
            response = await self.send_command("STATUS")

            if response == "IDLE":
                return {
                    "connected": True,
                    "status": "idle",
                    "message": "대기 중"
                }
            elif response.startswith("ACTIVE"):
                parts = response.split(':')
                return {
                    "connected": True,
                    "status": "active",
                    "mode": parts[1] if len(parts) > 1 else "unknown",
                    "remaining_seconds": int(parts[2]) if len(parts) > 2 else 0,
                    "message": "테라피 진행 중"
                }
            elif response == "COMPLETED":
                return {
                    "connected": True,
                    "status": "completed",
                    "message": "테라피 완료"
                }
            else:
                return {
                    "connected": True,
                    "status": "unknown",
                    "raw_response": response
                }

        except Exception as e:
            logger.error(f"상태 조회 실패: {e}")
            return {
                "connected": False,
                "error": str(e)
            }

    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self.client is not None and self.client.is_connected


# 싱글톤 인스턴스
_ble_service_instance: Optional[BLEDeviceService] = None


def get_ble_service() -> BLEDeviceService:
    """BLE 서비스 싱글톤 인스턴스 획득"""
    global _ble_service_instance
    if _ble_service_instance is None:
        if not BLEAK_AVAILABLE:
            raise ImportError("BLE를 사용할 수 없습니다. Mock 서비스를 사용하세요.")
        _ble_service_instance = BLEDeviceService()
    return _ble_service_instance
