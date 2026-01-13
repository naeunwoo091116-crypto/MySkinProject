"""
디바이스 설정 API 라우트
"""
import asyncio
import os
from flask import Blueprint, jsonify, request
from services.led_service import LEDService
from utils.decorators import handle_errors

# 연결 모드 결정: 시리얼(USB) > BLE > Mock
CONNECTION_MODE = None
device_service = None

# 1. 시리얼(USB) 연결 시도
try:
    from services.serial_service import get_serial_service
    device_service = get_serial_service()
    CONNECTION_MODE = "SERIAL"
    print("[INFO] USB serial mode enabled (wired connection)")
except Exception as e:
    print(f"[WARNING] Serial connection unavailable: {e}")

# 2. 시리얼 실패 시 BLE 시도
if CONNECTION_MODE is None:
    try:
        from services.ble_service import get_ble_service
        device_service = get_ble_service
        CONNECTION_MODE = "BLE"
        print("[INFO] BLE wireless mode enabled")
    except Exception as e:
        print(f"[WARNING] BLE connection unavailable: {e}")

# 3. 모두 실패 시 Mock 모드
if CONNECTION_MODE is None:
    try:
        from services.ble_service_mock import get_ble_service_mock
        device_service = get_ble_service_mock
        CONNECTION_MODE = "MOCK"
        print("[WARNING] Mock mode activated - simulation only")
        print("   (USB cable or Bluetooth required for real hardware connection)")
    except Exception as e:
        print(f"[CRITICAL ERROR] All connection modes failed")
        raise

print(f"[DEVICE] Current connection mode: {CONNECTION_MODE}")

device_bp = Blueprint('device', __name__)


def get_device_service():
    """디바이스 서비스 획득 (시리얼/BLE/Mock)"""
    if CONNECTION_MODE == "SERIAL":
        return device_service
    elif CONNECTION_MODE == "BLE":
        return device_service()
    elif CONNECTION_MODE == "MOCK":
        return device_service()
    else:
        raise RuntimeError("디바이스 서비스를 사용할 수 없습니다")


@device_bp.route('/api/v1/device/config', methods=['GET'])
@handle_errors
def get_device_config():
    """디바이스 설정 조회"""
    config = LEDService.get_device_config()
    return jsonify(config)


@device_bp.route('/api/v1/device/modes', methods=['GET'])
@handle_errors
def get_led_modes():
    """LED 모드 정보 조회"""
    modes = LEDService.get_led_modes()
    return jsonify(modes)


@device_bp.route('/api/v1/ble/scan', methods=['GET'])
@handle_errors
def scan_ble_devices():
    """디바이스 스캔"""
    service = get_device_service()

    if CONNECTION_MODE == "SERIAL":
        devices = service.scan_devices()
    elif CONNECTION_MODE in ["BLE", "MOCK"]:
        timeout = request.args.get('timeout', 10, type=int)
        devices = asyncio.run(service.scan_devices(timeout=timeout))
    else:
        devices = []

    return jsonify({
        "success": True,
        "devices": devices,
        "count": len(devices),
        "mode": CONNECTION_MODE
    })


@device_bp.route('/api/v1/ble/connect', methods=['POST'])
@handle_errors
def connect_ble_device():
    """디바이스 연결"""
    data = request.get_json() or {}
    service = get_device_service()

    # Mock 또는 SERIAL 모드인 경우 실제 LED 디바이스가 없으므로 연결 실패
    if CONNECTION_MODE == "MOCK":
        return jsonify({
            "success": False,
            "message": "실제 디바이스가 연결되어 있지 않습니다. USB 또는 BLE 디바이스를 연결해주세요.",
            "mode": CONNECTION_MODE,
            "is_mock": True
        }), 400

    # SERIAL 모드는 보통 휴대폰 USB 모뎀이므로 연결 거부
    if CONNECTION_MODE == "SERIAL":
        return jsonify({
            "success": False,
            "message": "LED 마스크가 연결되어 있지 않습니다. BLE 디바이스를 사용해주세요.",
            "mode": CONNECTION_MODE,
            "is_serial": True
        }), 400

    if CONNECTION_MODE == "BLE":
        address = data.get('address')
        success = asyncio.run(service.connect(address))
        address = getattr(service, 'device_address', None)
    else:
        success = False
        address = None

    if success:
        return jsonify({
            "success": True,
            "message": f"디바이스 연결 성공 ({CONNECTION_MODE} 모드)",
            "address": address,
            "mode": CONNECTION_MODE,
            "device_name": getattr(service, 'device_name', 'MySkin_LED_Mask')
        })
    else:
        return jsonify({
            "success": False,
            "message": "디바이스 연결 실패"
        }), 500


@device_bp.route('/api/v1/ble/disconnect', methods=['POST'])
@handle_errors
def disconnect_ble_device():
    """디바이스 연결 해제"""
    service = get_device_service()

    if CONNECTION_MODE == "SERIAL":
        service.disconnect()
    elif CONNECTION_MODE in ["BLE", "MOCK"]:
        asyncio.run(service.disconnect())

    return jsonify({
        "success": True,
        "message": "디바이스 연결 해제 완료"
    })


@device_bp.route('/api/v1/ble/status', methods=['GET'])
@handle_errors
def get_ble_status():
    """디바이스 상태 조회"""
    service = get_device_service()

    if CONNECTION_MODE == "SERIAL":
        status = service.get_status()
    elif CONNECTION_MODE in ["BLE", "MOCK"]:
        status = asyncio.run(service.get_status())
    else:
        status = {"connected": False}

    status["mode"] = CONNECTION_MODE
    return jsonify(status)


@device_bp.route('/api/v1/ble/therapy/start', methods=['POST'])
@handle_errors
def start_therapy():
    """LED 테라피 시작"""
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "요청 데이터가 없습니다"
        }), 400

    mode = data.get('mode')
    duration = data.get('duration')

    if not mode or not duration:
        return jsonify({
            "success": False,
            "message": "mode와 duration이 필요합니다"
        }), 400

    service = get_device_service()

    if not service.is_connected():
        return jsonify({
            "success": False,
            "message": "디바이스가 연결되지 않았습니다"
        }), 400

    if CONNECTION_MODE == "SERIAL":
        result = service.start_therapy(mode, duration)
    elif CONNECTION_MODE in ["BLE", "MOCK"]:
        result = asyncio.run(service.start_therapy(mode, duration))
    else:
        result = {"success": False, "message": "지원하지 않는 연결 모드"}

    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 500


@device_bp.route('/api/v1/ble/therapy/stop', methods=['POST'])
@handle_errors
def stop_therapy():
    """LED 테라피 중지"""
    service = get_device_service()

    if not service.is_connected():
        return jsonify({
            "success": False,
            "message": "디바이스가 연결되지 않았습니다"
        }), 400

    if CONNECTION_MODE == "SERIAL":
        result = service.stop_therapy()
    elif CONNECTION_MODE in ["BLE", "MOCK"]:
        result = asyncio.run(service.stop_therapy())
    else:
        result = {"success": False, "message": "지원하지 않는 연결 모드"}

    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 500
