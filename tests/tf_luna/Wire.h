#pragma once
#include <cstdint>
#include <string>
#include <sstream>
#include <vector>
#define F(x) x
#define HEX 16
using String = class FakeString {
  std::string value;
public:
  FakeString(const char* s):value(s){}
  bool operator==(const char* s) const {return value==s;}
  bool startsWith(const char* s) const {return value.rfind(s,0)==0;}
};
static uint32_t clock_ms=0;
uint32_t millis(){return clock_ms;}
struct FakeSerial {
  std::ostringstream text;
  template<class T> void print(T x){text<<x;}
  void print(uint8_t x){text<<unsigned(x);}
  void print(uint8_t x,int){text<<std::hex<<unsigned(x)<<std::dec;}
  template<class T> void println(T x){print(x);text<<'\n';}
} Serial;
struct FakeWire {
  uint8_t memory[128][256]={};
  uint8_t addr=0,reg=0,index=0,received=0;
  bool nack=false,timeout=false,inject_timeout=false;
  int short_read=-1,calls=0;
  std::vector<uint8_t> tx;
  void begin(){} void setClock(unsigned long){} void setWireTimeout(unsigned long,bool){}
  void clearWireTimeoutFlag(){timeout=false;}
  bool getWireTimeoutFlag(){return timeout;}
  void beginTransmission(uint8_t a){addr=a;tx.clear();++calls;}
  void write(uint8_t x){tx.push_back(x);}
  uint8_t endTransmission(bool=true){
    if(inject_timeout){timeout=true;return 5;}
    if(nack)return 2;
    reg=tx[0];if(tx.size()>1)memory[addr][reg]=tx[1];return 0;
  }
  uint8_t requestFrom(uint8_t a,uint8_t count){
    addr=a;index=0;received=short_read<0?count:uint8_t(short_read);return received;
  }
  uint8_t available(){return received-index;}
  uint8_t read(){return memory[addr][uint8_t(reg+index++)];}
} Wire;
