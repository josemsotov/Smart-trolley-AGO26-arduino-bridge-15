#ifndef TF_LUNA_H
#define TF_LUNA_H

#include <Wire.h>

// Benewake TF-Luna manual, April 2024, sections 6.3 / Appendix III.
// No heap allocation, EEPROM writes, address changes, or motor commands.
enum TfPhase : uint8_t { TF_IDENTIFY, TF_MODE, TF_VERIFY, TF_ENABLE,
                         TF_BASELINE, TF_TRIGGER, TF_READ };
enum TfError : uint8_t { TF_OK, TF_OFF, TF_BUS, TF_ID, TF_CONFIG,
                         TF_NOT_NEW, TF_SIGNAL, TF_RANGE, TF_DEVICE };
struct TfLunaState {
  uint32_t due, last_sample;
  uint16_t cm, amp, tick, device_error, errors;
  uint8_t address, phase, error;
  bool enabled, valid;
};
static TfLunaState tf_luna[2] = {};

static uint16_t tf_u16(const uint8_t *b) {
  return (uint16_t)b[0] | ((uint16_t)b[1] << 8);
}
static bool tf_read(uint8_t address, uint8_t reg, uint8_t *b, uint8_t count) {
  Wire.clearWireTimeoutFlag();
  Wire.beginTransmission(address);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0 || Wire.getWireTimeoutFlag()) return false;
  uint8_t got = Wire.requestFrom(address, count);
  if (got != count || Wire.getWireTimeoutFlag()) {
    while (Wire.available()) Wire.read();
    return false;
  }
  for (uint8_t i=0; i<count; ++i) b[i] = Wire.read();
  return true;
}
static bool tf_write(uint8_t address, uint8_t reg, uint8_t value) {
  Wire.clearWireTimeoutFlag();
  Wire.beginTransmission(address); Wire.write(reg); Wire.write(value);
  return Wire.endTransmission() == 0 && !Wire.getWireTimeoutFlag();
}
static void tf_fail(TfLunaState &s, uint8_t error, uint32_t now) {
  s.valid=false; s.error=error; s.phase=TF_IDENTIFY;
  if (s.errors != 65535U) ++s.errors;
  s.due=now+TF_LUNA_RETRY_MS;
}
void tf_luna_initialize() {
  // Preserve shared MPU clock/timeout configuration when already initialized.
  #ifndef ENABLE_MPU9250
    Wire.begin(); Wire.setClock(400000); Wire.setWireTimeout(3000, true);
  #endif
  tf_luna[0].address=TF_LUNA_ADDR_1; tf_luna[1].address=TF_LUNA_ADDR_2;
  for (uint8_t i=0;i<2;++i) { tf_luna[i].enabled=false; tf_luna[i].error=TF_OFF; }
}
void tf_luna_status(uint8_t i) {
  TfLunaState &s=tf_luna[i];
  bool fresh=s.valid && (uint32_t)(millis()-s.last_sample)<=TF_LUNA_STALE_MS;
  Serial.print(F("TF id=")); Serial.print(i+1);
  Serial.print(F(" addr=0x")); Serial.print(s.address,HEX);
  Serial.print(F(" enabled=")); Serial.print(s.enabled);
  Serial.print(F(" valid=")); Serial.print(fresh);
  Serial.print(F(" cm=")); Serial.print(s.cm);
  Serial.print(F(" amp=")); Serial.print(s.amp);
  Serial.print(F(" tick=")); Serial.print(s.tick);
  Serial.print(F(" device_error=")); Serial.print(s.device_error);
  Serial.print(F(" err=")); Serial.print(s.error);
  Serial.print(F(" faults=")); Serial.println(s.errors);
}
void tf_luna_command(String cmd) {
  if (cmd=="tf" || cmd=="tf status") {
    tf_luna_status(0); tf_luna_status(1); return;
  }
  // Exact syntax prevents malformed IDs silently selecting the first sensor.
  uint8_t id;
  if (cmd=="tf on 1" || cmd=="tf off 1") id=0;
  else if (cmd=="tf on 2" || cmd=="tf off 2") id=1;
  else { Serial.println(F("tf usage: tf status | tf on 1|2 | tf off 1|2")); return; }
  bool enable=cmd.startsWith("tf on ");
  // Restrict commissioning to stationary robot, including pulse-density OFF gaps.
  if (enable && (leftMotor.pwm!=0 || rightMotor.pwm!=0 ||
      currentRobotState==STATE_HABILITADO)) {
    Serial.println(F("tf FAIL disable motors first")); return;
  }
  TfLunaState &s=tf_luna[id];
  s.enabled=enable; s.valid=false; s.error=enable ? TF_NOT_NEW : TF_OFF;
  s.phase=TF_IDENTIFY; s.due=millis();
  tf_luna_status(id);
}
void tf_luna_update() {
  static uint8_t next=0;
  uint32_t now=millis();
  // At most one channel/transaction step per loop. Wire timeout bounds bus stalls
  // (a read contains a register-pointer write and a read, each up to 3 ms).
  for (uint8_t checked=0; checked<2; ++checked) {
    uint8_t i=next; next=(next+1)%2;
    TfLunaState &s=tf_luna[i];
    if (!s.enabled || (int32_t)(now-s.due)<0) continue;
    uint8_t b[10];
    switch (s.phase) {
      case TF_IDENTIFY:
        if (!tf_read(s.address,0x3C,b,4)) { tf_fail(s,TF_BUS,now); break; }
        if (b[0]!='L'||b[1]!='U'||b[2]!='N'||b[3]!='A') { tf_fail(s,TF_ID,now); break; }
        s.phase=TF_MODE; s.due=now; break;
      case TF_MODE:
        if (!tf_write(s.address,0x23,1)) { tf_fail(s,TF_BUS,now); break; }
        s.phase=TF_VERIFY; s.due=now+TF_LUNA_WAIT_MS; break;
      case TF_VERIFY:
        if (!tf_read(s.address,0x23,b,1)) { tf_fail(s,TF_BUS,now); break; }
        if (b[0]!=1) { tf_fail(s,TF_CONFIG,now); break; }
        s.phase=TF_ENABLE; s.due=now; break;
      case TF_ENABLE:
        if (!tf_write(s.address,0x25,1)) { tf_fail(s,TF_BUS,now); break; }
        s.phase=TF_BASELINE; s.due=now+TF_LUNA_WAIT_MS; break;
      case TF_BASELINE:
        if (!tf_read(s.address,0x06,b,2)) { tf_fail(s,TF_BUS,now); break; }
        s.tick=tf_u16(b); s.phase=TF_TRIGGER; s.due=now; break;
      case TF_TRIGGER:
        if (!tf_write(s.address,0x24,1)) { tf_fail(s,TF_BUS,now); break; }
        s.phase=TF_READ; s.due=now+TF_LUNA_WAIT_MS; break;
      case TF_READ:
        if (!tf_read(s.address,0x00,b,10)) { tf_fail(s,TF_BUS,now); break; }
        if (tf_u16(b+6)==s.tick) { tf_fail(s,TF_NOT_NEW,now); break; }
        s.tick=tf_u16(b+6); s.cm=tf_u16(b); s.amp=tf_u16(b+2);
        s.device_error=tf_u16(b+8); s.last_sample=now;
        s.error=s.device_error ? TF_DEVICE :
          (s.amp<100 || s.amp>=32768) ? TF_SIGNAL :
          (s.cm<20 || s.cm>800) ? TF_RANGE : TF_OK;
        s.valid=s.error==TF_OK;
        s.phase=TF_TRIGGER; s.due=now+100UL;
        break;
    }
    // Reporting only by explicit tf status: no extra serial load on motion loop.
    break;
  }
}
#endif
