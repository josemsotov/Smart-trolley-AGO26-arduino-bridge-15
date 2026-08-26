#!/usr/bin/env python3
"""Bench-only fused Hall/opto PI test with guaranteed serial stop."""
import re
import time

import serial


PORT = "/dev/ttyACM0"
RUN_SECONDS = 6.0
CMD = "v 0.100 0.000"
STATUS_RE = re.compile(
    r"T .*Lpwm=(\d+) Rpwm=(\d+).*Lrpm=(\d+) Rrpm=(\d+) "
    r"Lfrpm=(\d+) Rfrpm=(\d+) Lfs=([FH]) Rfs=([FH]).*PI=(\d+)"
)


def send(ser, command):
    ser.write((command + "\n").encode())
    ser.flush()
    time.sleep(0.05)


def main():
    samples = []
    messages = []
    with serial.Serial(PORT, 115200, timeout=0.10, write_timeout=5.0) as ser:
        time.sleep(7.0)
        try:
            send(ser, "STOP")
            send(ser, "INHABILITAR")
            send(ser, "n selftest")
            send(ser, "r")
            send(ser, "k 0.15 0.0")
            send(ser, "k on")
            start = time.monotonic()
            last_command = 0.0
            while time.monotonic() - start < RUN_SECONDS:
                now = time.monotonic()
                if now - last_command >= 0.08:
                    send(ser, CMD)
                    last_command = now
                line = ser.readline().decode(errors="replace").strip()
                if not line:
                    continue
                if "SELFTEST" in line or line.startswith("k "):
                    messages.append(line)
                match = STATUS_RE.search(line)
                if match:
                    values = match.groups()
                    samples.append({
                        "lpwm": int(values[0]), "rpwm": int(values[1]),
                        "lrpm": int(values[2]), "rrpm": int(values[3]),
                        "lfrpm": int(values[4]), "rfrpm": int(values[5]),
                        "lfs": values[6], "rfs": values[7],
                        "pi": int(values[8]),
                    })
        finally:
            send(ser, "v 0.0 0.0")
            send(ser, "STOP")
            send(ser, "k off")
            send(ser, "INHABILITAR")
            time.sleep(0.5)

    print("MESSAGES")
    for message in messages:
        print(message)
    print(f"SAMPLES={len(samples)}")
    for sample in samples:
        print(sample)
    fused_left = sum(sample["lfs"] == "F" for sample in samples)
    fused_right = sum(sample["rfs"] == "F" for sample in samples)
    print(f"FUSED_LEFT={fused_left}/{len(samples)}")
    print(f"FUSED_RIGHT={fused_right}/{len(samples)}")


if __name__ == "__main__":
    main()
