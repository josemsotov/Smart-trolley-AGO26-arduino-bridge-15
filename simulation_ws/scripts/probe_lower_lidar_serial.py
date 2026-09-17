"""Read bytes only after the lower ROS driver has exited. No commands sent."""
import json
import time
import serial

port = '/dev/serial/by-path/platform-xhci-hcd.1-usb-0:1.4:1.0-port0'
with serial.Serial(port, 230400, timeout=0.2, exclusive=True) as device:
    data = bytearray()
    end = time.monotonic() + 5
    while time.monotonic() < end:
        data.extend(device.read(4096))
print(json.dumps({'port': port, 'baud': 230400, 'bytes_in_5s': len(data),
                  'ld_packet_headers_54_2c': data.count(b'\x54\x2c'),
                  'first_48_bytes_hex': data[:48].hex()}))
