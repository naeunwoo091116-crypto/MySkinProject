"""
USB 시리얼 통신 서비스
Seeed Xiao BLE와 USB 케이블로 직접 연결
"""
import serial
import serial.tools.list_ports
import time
from typing import Optional, Dict, Any, List
from core.logger import setup_logger
from core.constants import DEVICE_CONFIG

logger = setup_logger(__name__)


class SerialDeviceService:
    """시리얼 디바이스 통신 서비스"""

    def __init__(self):
        self.device_name = DEVICE_CONFIG["device_name"]
        self.serial_port: Optional[serial.Serial] = None
        self.port_name: Optional[str] = None
        self.baud_rate = 115200
        self._connected = False

    def scan_devices(self) -> List[Dict[str, str]]:
        """
        사용 가능한 시리얼 포트 스캔

        Returns:
            포트 리스트
        """
        logger.info("시리얼 포트 스캔 시작")

        ports = serial.tools.list_ports.comports()
        available_ports = []

        for port in ports:
            port_info = {
                "port": port.device,
                "description": port.description,
                "hwid": port.hwid
            }
            available_ports.append(port_info)
            logger.info(f"발견된 포트: {port.device} - {port.description}")

        logger.info(f"{len(available_ports)}개의 시리얼 포트 발견")
        return available_ports

    def connect(self, port: Optional[str] = None) -> bool:
        """
        시리얼 포트 연결

        Args:
            port: 포트 이름 (None이면 자동 검색)

        Returns:
            연결 성공 여부
        """
        if self._connected and self.serial_port and self.serial_port.is_open:
            logger.info("이미 연결된 포트가 있습니다")
            return True

        try:
            # 포트가 지정되지 않으면 자동 검색
            if port is None:
                ports = self.scan_devices()
                if not ports:
                    logger.error("사용 가능한 시리얼 포트가 없습니다")
                    return False

                # Arduino/Seeed 장치 우선 선택
                for p in ports:
                    desc_lower = p['description'].lower()
                    if 'arduino' in desc_lower or 'ch340' in desc_lower or 'usb serial' in desc_lower:
                        port = p['port']
                        logger.info(f"Arduino 포트 자동 선택: {port}")
                        break

                # 없으면 첫 번째 포트 사용
                if port is None:
                    port = ports[0]['port']
                    logger.info(f"첫 번째 포트 선택: {port}")

            logger.info(f"시리얼 포트 연결 시도: {port} @ {self.baud_rate} baud")

            # 시리얼 포트 열기
            self.serial_port = serial.Serial(
                port=port,
                baudrate=self.baud_rate,
                timeout=2,
                write_timeout=2
            )

            # 연결 안정화 대기
            time.sleep(2)

            # 아두이노 리셋 후 초기화 메시지 읽기
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()

            self._connected = True
            self.port_name = port
            logger.info(f"시리얼 포트 연결 성공: {port}")

            return True

        except serial.SerialException as e:
            logger.error(f"시리얼 포트 연결 실패: {e}")
            self.serial_port = None
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            self.serial_port = None
            self._connected = False
            return False

    def disconnect(self):
        """시리얼 포트 연결 해제"""
        if self.serial_port and self.serial_port.is_open:
            try:
                # STOP 명령 전송 후 닫기
                self.send_command("STOP")
                time.sleep(0.5)
                self.serial_port.close()
                logger.info("시리얼 포트 연결 해제 완료")
            except Exception as e:
                logger.error(f"연결 해제 오류: {e}")
            finally:
                self.serial_port = None
                self._connected = False
                self.port_name = None

    def send_command(self, command: str) -> str:
        """
        시리얼로 명령 전송

        Args:
            command: 전송할 명령 문자열

        Returns:
            아두이노 응답
        """
        if not self._connected or not self.serial_port or not self.serial_port.is_open:
            raise ConnectionError("시리얼 포트가 연결되지 않았습니다")

        try:
            logger.info(f"명령 전송: {command}")

            # 명령 전송 (줄바꿈 포함)
            self.serial_port.write((command + '\n').encode('utf-8'))
            self.serial_port.flush()

            # 응답 대기
            time.sleep(0.3)

            # 응답 읽기
            response = ""
            if self.serial_port.in_waiting > 0:
                response = self.serial_port.readline().decode('utf-8').strip()

            if not response:
                response = "OK"

            logger.info(f"아두이노 응답: {response}")
            return response

        except Exception as e:
            logger.error(f"명령 전송 오류: {e}")
            raise

    def start_therapy(self, mode: str, duration: int) -> Dict[str, Any]:
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
            response = self.send_command(command)

            if response.startswith("OK:STARTED") or response == "OK":
                return {
                    "success": True,
                    "mode": mode.upper(),
                    "duration": duration,
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
                    "success": True,
                    "mode": mode.upper(),
                    "duration": duration,
                    "message": "테라피가 시작되었습니다"
                }

        except Exception as e:
            logger.error(f"테라피 시작 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "테라피 시작 중 오류 발생"
            }

    def stop_therapy(self) -> Dict[str, Any]:
        """
        LED 테라피 중지

        Returns:
            응답 딕셔너리
        """
        try:
            response = self.send_command("STOP")

            if response.startswith("OK") or "STOP" in response:
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

    def get_status(self) -> Dict[str, Any]:
        """
        디바이스 상태 조회

        Returns:
            상태 딕셔너리
        """
        if not self._connected or not self.serial_port or not self.serial_port.is_open:
            return {
                "connected": False,
                "status": "disconnected"
            }

        try:
            response = self.send_command("STATUS")

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
                    "status": "idle",
                    "message": "대기 중"
                }

        except Exception as e:
            logger.error(f"상태 조회 실패: {e}")
            return {
                "connected": False,
                "error": str(e)
            }

    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self._connected and self.serial_port is not None and self.serial_port.is_open


# 싱글톤 인스턴스
_serial_service_instance: Optional[SerialDeviceService] = None


def get_serial_service() -> SerialDeviceService:
    """시리얼 서비스 싱글톤 인스턴스 획득"""
    global _serial_service_instance
    if _serial_service_instance is None:
        _serial_service_instance = SerialDeviceService()
    return _serial_service_instance
