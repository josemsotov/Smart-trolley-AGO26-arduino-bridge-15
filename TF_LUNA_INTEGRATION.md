# TF-Luna commissioning firmware — 2026-09-13

Obstacle bench testing paused at user request. This change is local firmware
support only. No motors commanded during commissioning.

## Scope

- `TF_Luna.h`, included by `Modules.h` with `ENABLE_TF_LUNA`.
- Two channels, 7-bit addresses0x10 and0x11 in Configuration.h.
- Both runtime-disabled at every Arduino boot; no TF transactions until enabled.
- Command handling before legacy uppercase conversion, through ros2_tryProcessCommand.
- No modification of motor gains, encoder filters, heading or safety commands.
- No extra library beyond existing Arduino Wire. No dynamic driver buffers.
- Not used for obstacle braking, ROS Range messages or UI indicators yet.
  Existing bridge raw serial telemetry can carry the text response.

## Electrical connection — power OFF before wiring

Use bidirectional I2C level translation: Arduino bus on appropriate high side,
TF-Luna signals on3.3V low side, common GND. Existing SDA/SCL measured3.93V:
do NOT connect TF signals directly. Verify MPU board level compatibility too.

| TF-Luna connector pin | Connection |
|---|---|
| 1 | Regulated5V supply, not a digital GPIO |
| 2 SDA | Adapter low-side SDA; high side to Mega D20 |
| 3 SCL | Adapter low-side SCL; high side to Mega D21 |
| 4 | Common GND |
| 5 | GND to select I2C |
| 6 | Unused in this triggered implementation; leave unconnected |

Confirm connector orientation from manual figure4, not cable colors alone.
Two TF-Lunas may require300mA combined peak. Use an adequately rated regulated
source; do not parallel its5V output with USB-powered Mega5V indiscriminately.
Adapter LV needs regulated3.3V; a level shifter does not generate that supply.

## Commands (lowercase)

| Command | Meaning |
|---|---|
| `tf status` or `tf` | Print both channels; does not access I2C |
| `tf on 1` | Enable commissioning channel1, address0x10 |
| `tf off 1` | Stop host polling, immediately invalidate channel1 |
| `tf on 2` / `tf off 2` | Same for channel2, address0x11 |

Enabling is rejected while motors report PWM or state STATE_HABILITADO, even
if a pulse-density gap currently outputs0. Start with robot disabled/stationary.
Off is always accepted. Driver commands do not enable or actuate motors.
Off does not power down the physical module or undo its runtime trigger mode.

Responses:
`TF id=1 addr=0x10 enabled=1 valid=1 cm=123 amp=200 tick=... device_error=0 err=0 faults=0`
Values here are an example, not a hardware measurement. A consumer MUST check
valid, not just cm: old numbers are retained for diagnosis after invalidation.
Status considers samples older than500ms invalid. No unsolicited TF stream is
added; poll status sparingly (e.g.2Hz) to preserve serial bandwidth.

Error codes:0=OK,1=off,2=I2C/timeout/short read,3=wrong signature,
4=mode verification failed,5=timestamp unchanged/not yet acquired,
6=signal weak/overexposed,7=outside20..800cm,8=device error register nonzero.
faults counts transport/protocol recovery events, not every invalid measurement.

## Protocol and timing

Based on supplied Benewake manual: sections6.3/6.6, AppendixIII printed32–33.
Verify0x3C..0x3F=`LUNA` before configuration. Write0x23=1 (trigger mode),
wait100ms and verify; write0x25=1 (enable), wait100ms; read initial timestamp.
Write0x24=1 to trigger, wait100ms; read10 bytes from0x00 (distance, amplitude,
temperature bytes ignored, tick, device error). Require tick change. Then wait
100ms before next trigger: ~5Hz per channel, subject to main-loop workload.
Read distances as little-endian centimeters. Reject amplitude<100 or>=32768,
distance<20 or>800cm, device errors and unchanged ticks. Valid signal/range does
not establish material-dependent accuracy or outdoor performance.

No delay() in the sensor state machine. One channel step per loop, after motor
safety checks. Shared Wire uses existing400kHz/3000us timeout with MPU; a read
has two transactions, so worst-case wait is not zero (~6ms transport bound).
Bus errors invalidate immediately and retry identification after1s.
Timeouts cannot make a physically shorted shared I2C bus safe; hardware and
IMU timing under load still need validation. Repeated status also costs serial time.

No SAVE0x20 writes, no address0x22 writes, no sensor reboot commands, no bus scan.
For two units, assign the second unit0x11 separately, one sensor at a time,
save and verify after its reboot. Merely changing TF_LUNA_ADDR_2 does NOT change
the device address. Do not connect two factory-default0x10 units simultaneously.

## Verification performed / remaining

Mega build:68780 bytes flash,7125/8192 RAM,1067 free. Low-memory warning remains.
Artifact: `.codex_build_tfluna/MOTOR-INTERFACE-V14.ino.hex` (build output ignored
by Git). Artifact SHA256:
`3fa43156fcc0d0c2456cde10084b70045d81070851e02c8961f07dde01ba902e`.

Before flashing, the previous Arduino flash was backed up on the Pi:
`/home/josemsotov/robot_backups/pre_tfluna_20260913_foCkza/original.hex`.
Backup SHA256:
`dfd72ef56f1fff65636438b1c88b4991ccf52e7ffef550453e931b8f2fa99fbd`.
Local copy:
`arduino_flash_backups/pre_tfluna_20260913_original.hex`.

After the Arduino Mega USB device reappeared, the TF-Luna firmware was flashed
and verified successfully with `avrdude`:

- 68780 bytes written.
- 68780 bytes verified against `/tmp/tfluna_20260913.hex`.
- Previous flash backup from the successful upload run:
  `/home/josemsotov/robot_backups/pre_tfluna_20260913_5jjaKY/original.hex`.
- That backup SHA256:
  `31170255871eeffa724f193b2e1cae259d177d026b25c27db85bff4444fc015b`.
- Local copy:
  `arduino_flash_backups/pre_tfluna_20260913_before_successful_upload.hex`.

Current hardware verification:

- `robot-follower.service` active after the test.
- Arduino Mega visible again as `/dev/ttyACM0`.
- Firmware recognizes `tf status`, `tf on 1`, `tf on 2`, and `tf off`.
- Channel1/address0x10 returns `enabled=1 valid=0 err=2`.
- Channel2/address0x11 also returns `enabled=1 valid=0 err=2`.
- IMU is intentionally disconnected for this test, so missing IMU data is
  expected until it is reconnected.

`err=2` means I2C/timeout/short-read/NACK at the Arduino bus level. This points
to wiring, level shifting, power, pin5 mode selection, sensor orientation, or a
different device address; it is not a distance/range quality failure.

Native C++ tests include the actual driver against fake Wire/Serial/motor state:
disabled boot/no polling, malformed command, motion interlock, NACK/backoff,
wrong signature, timeout, trigger registers/no save, valid frame, staleness,
weak/overexposed signal, range bounds, device error, short read, repeated tick,
tick wrap, millis wrap, disabling and channel2 selection. Tests passed via WSL.

Build/run from project cwd in WSL:
```
g++ -std=c++11 -Wall -Wextra -I tests/tf_luna tests/tf_luna/test_driver.cpp -o .codex_build_tfluna/test_driver
./.codex_build_tfluna/test_driver
```

Next: with power off, recheck TF-Luna VCC/GND, SDA/SCL through the level shifter,
pin5 tied to GND for I2C mode, LV=3.3V, HV=Arduino bus side, common ground, and
connector orientation. Then retry `tf on 1` and `tf status`. After the TF test,
reconnect the MPU and confirm MPU data and motor watchdog unaffected.
Mock tests cannot establish actual conversion latency, timestamp semantics,
sensor firmware compatibility, electrical safety or reliable ranging.
