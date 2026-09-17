#include <cassert>
#include <cstring>
#include <iostream>
#include "Wire.h"
#define ENABLE_MPU9250
#define TF_LUNA_ADDR_1 0x10
#define TF_LUNA_ADDR_2 0x11
#define TF_LUNA_WAIT_MS 100UL
#define TF_LUNA_RETRY_MS 1000UL
#define TF_LUNA_STALE_MS 500UL
struct Motor {int pwm=0;} leftMotor,rightMotor;
enum {STATE_INHABILITADO,STATE_HABILITADO};
int currentRobotState=STATE_INHABILITADO;
#include "../../TF_Luna.h"

void reset(){
  for(auto &s:tf_luna) { s={}; }
  Wire=FakeWire{};clock_ms=0;
  leftMotor.pwm=rightMotor.pwm=0;currentRobotState=STATE_INHABILITADO;
  tf_luna_initialize();
}
void signature(){memcpy(Wire.memory[0x10]+0x3c,"LUNA",4);}
void runstep(uint32_t advance=101){clock_ms+=advance;tf_luna_update();}
void word(uint8_t reg,uint16_t value){Wire.memory[0x10][reg]=value&255;Wire.memory[0x10][reg+1]=value>>8;}
void measurement(uint16_t cm,uint16_t amp,uint16_t tick,uint16_t error=0){word(0,cm);word(2,amp);word(6,tick);word(8,error);}
void ready(){
  reset();signature();tf_luna_command("tf on 1");
  for(int i=0;i<6;++i)runstep();
  assert(tf_luna[0].phase==TF_READ);
  assert(Wire.memory[0x10][0x23]==1);
  assert(Wire.memory[0x10][0x24]==1);
  assert(Wire.memory[0x10][0x20]==0); // never SAVE
  assert(Wire.memory[0x10][0x22]==0); // never change address
}
int main(){
  reset();for(int i=0;i<20;++i)runstep();assert(Wire.calls==0);
  tf_luna_command("tf on 3");assert(!tf_luna[0].enabled&&!tf_luna[1].enabled);
  currentRobotState=STATE_HABILITADO;tf_luna_command("tf on 1");assert(!tf_luna[0].enabled);
  reset();Wire.nack=true;tf_luna_command("tf on 1");runstep();assert(tf_luna[0].error==TF_BUS);
  int calls=Wire.calls;runstep();assert(Wire.calls==calls); // absent-device backoff
  reset();tf_luna_command("tf on 1");runstep();assert(tf_luna[0].error==TF_ID);
  reset();Wire.inject_timeout=true;tf_luna_command("tf on 1");runstep();assert(tf_luna[0].error==TF_BUS);
  ready();measurement(123,200,1);runstep();assert(tf_luna[0].valid&&tf_luna[0].cm==123);
  clock_ms+=501;Serial.text.str("");tf_luna_status(0);assert(Serial.text.str().find("valid=0")!=std::string::npos);
  ready();measurement(123,99,1);runstep();assert(tf_luna[0].error==TF_SIGNAL&&!tf_luna[0].valid);
  ready();measurement(123,32768,1);runstep();assert(tf_luna[0].error==TF_SIGNAL);
  ready();measurement(19,200,1);runstep();assert(tf_luna[0].error==TF_RANGE);
  ready();measurement(801,200,1);runstep();assert(tf_luna[0].error==TF_RANGE);
  ready();measurement(123,200,1,1);runstep();assert(tf_luna[0].error==TF_DEVICE);
  ready();measurement(123,200,0);runstep();assert(tf_luna[0].error==TF_NOT_NEW);
  ready();Wire.short_read=4;runstep();assert(tf_luna[0].error==TF_BUS);
  ready();tf_luna[0].tick=65535;measurement(123,200,0);runstep();assert(tf_luna[0].valid);
  tf_luna_command("tf off 1");calls=Wire.calls;runstep();assert(Wire.calls==calls&&!tf_luna[0].valid);
  reset();tf_luna_command("tf on 2");assert(tf_luna[1].enabled&&!tf_luna[0].enabled);
  reset();clock_ms=0xfffffff0U;signature();tf_luna_command("tf on 1");runstep(0);runstep(0);
  assert(tf_luna[0].phase==TF_VERIFY);runstep(50);assert(tf_luna[0].phase==TF_VERIFY);
  runstep(51);assert(tf_luna[0].phase==TF_ENABLE);
  std::cout<<"PASS: disabled boot, strict commands, motion interlock, NACK/backoff, ID, timeout, trigger, valid/stale data, signal/range/device faults, short read, tick/time wrap, off, second channel\n";
}
