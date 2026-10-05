#ifndef SERVO_CONTROL_H
#define SERVO_CONTROL_H

#ifdef ENABLE_AUX_SERVO

#include <Arduino.h>
#include <avr/interrupt.h>
#include <util/atomic.h>

#define AUX_SERVO_TIMER_PRESCALER 8UL
#define AUX_SERVO_FRAME_US 20000UL
#define AUX_SERVO_TICKS_PER_US (F_CPU / AUX_SERVO_TIMER_PRESCALER / 1000000UL)
#define AUX_SERVO_FRAME_TICKS (AUX_SERVO_FRAME_US * AUX_SERVO_TICKS_PER_US)

#if AUX_SERVO_FRAME_TICKS > 65535UL
  #error "La configuracion de Timer1 del servo excede 16 bits"
#endif

volatile uint16_t auxServoPulseTicks =
    AUX_SERVO_MIN_PULSE_US * AUX_SERVO_TICKS_PER_US;
volatile bool auxServoPulseHigh = false;
volatile uint8_t auxServoPin = AUX_SERVO_PIN;
int auxServoAngle = AUX_SERVO_START_ANGLE;

ISR(TIMER1_COMPA_vect) {
  if (auxServoPulseHigh) {
    digitalWrite(auxServoPin, LOW);
    OCR1A = static_cast<uint16_t>(
        AUX_SERVO_FRAME_TICKS - auxServoPulseTicks - 1UL);
    auxServoPulseHigh = false;
  } else {
    digitalWrite(auxServoPin, HIGH);
    OCR1A = auxServoPulseTicks - 1U;
    auxServoPulseHigh = true;
  }
}

void aux_servo_set_angle(int angle) {
  const int constrainedAngle =
      constrain(angle, AUX_SERVO_MIN_ANGLE, AUX_SERVO_MAX_ANGLE);
  const uint16_t pulseUs = static_cast<uint16_t>(map(
      constrainedAngle,
      AUX_SERVO_MIN_ANGLE,
      AUX_SERVO_MAX_ANGLE,
      AUX_SERVO_MIN_PULSE_US,
      AUX_SERVO_MAX_PULSE_US));
  const uint16_t pulseTicks =
      pulseUs * static_cast<uint16_t>(AUX_SERVO_TICKS_PER_US);

  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
    auxServoPulseTicks = pulseTicks;
  }
  auxServoAngle = constrainedAngle;
}

void aux_servo_initialize() {
  pinMode(auxServoPin, OUTPUT);
  digitalWrite(auxServoPin, LOW);
  aux_servo_set_angle(AUX_SERVO_START_ANGLE);

  const uint8_t savedSreg = SREG;
  cli();
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 0;
  OCR1A = static_cast<uint16_t>(AUX_SERVO_FRAME_TICKS - 1UL);
  TIFR1 = _BV(OCF1A);
  TIMSK1 = _BV(OCIE1A);
  TCCR1B = _BV(WGM12) | _BV(CS11);
  SREG = savedSreg;

  Serial.print(F("SERVO READY pin="));
  Serial.print(auxServoPin);
  Serial.print(F(" angle="));
  Serial.println(auxServoAngle);
}

void aux_servo_print_status() {
  Serial.print(F("SERVO angle="));
  Serial.print(auxServoAngle);
  Serial.print(F(" pin="));
  Serial.print(auxServoPin);
  Serial.println(F(" timer=1"));
}

bool aux_servo_is_diagnostic_pin(int pin) {
  return pin == 34 || pin == 36 || pin == 38 || pin == 40 || pin == 42;
}

void aux_servo_set_pin(int requestedPin) {
  if (!aux_servo_is_diagnostic_pin(requestedPin)) {
    Serial.println(F("ERROR SERVO: usa PIN 34, 36, 38, 40 o 42"));
    return;
  }

  const uint8_t nextPin = static_cast<uint8_t>(requestedPin);
  const uint8_t previousPin = auxServoPin;
  if (nextPin != previousPin) {
    pinMode(nextPin, OUTPUT);
    digitalWrite(nextPin, LOW);
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
      auxServoPin = nextPin;
    }
    digitalWrite(previousPin, LOW);
    pinMode(previousPin, INPUT);
  }
  aux_servo_print_status();
}

void aux_servo_toggle() {
  const int nextAngle =
      auxServoAngle == AUX_SERVO_TOGGLE_ANGLE
          ? AUX_SERVO_START_ANGLE
          : AUX_SERVO_TOGGLE_ANGLE;
  aux_servo_set_angle(nextAngle);
  aux_servo_print_status();
}

void aux_servo_process_command(const String &command) {
  if (command == "SERVO TOGGLE") {
    aux_servo_toggle();
    return;
  }
  if (command == "SERVO STATUS") {
    aux_servo_print_status();
    return;
  }
  if (command.startsWith("SERVO PIN ")) {
    String pinText = command.substring(10);
    pinText.trim();
    for (unsigned int i = 0; i < pinText.length(); ++i) {
      if (pinText.charAt(i) < '0' || pinText.charAt(i) > '9') {
        Serial.println(F("ERROR SERVO: pin invalido"));
        return;
      }
    }
    aux_servo_set_pin(pinText.toInt());
    return;
  }
  if (!command.startsWith("SERVO ")) {
    Serial.println(F(
        "ERROR SERVO: usa SERVO <0-180>, TOGGLE, STATUS o PIN <n>"));
    return;
  }

  String angleText = command.substring(6);
  angleText.trim();
  if (angleText.length() == 0) {
    Serial.println(F("ERROR SERVO: falta el angulo"));
    return;
  }
  for (unsigned int i = 0; i < angleText.length(); ++i) {
    if (angleText.charAt(i) < '0' || angleText.charAt(i) > '9') {
      Serial.println(F(
          "ERROR SERVO: el angulo debe ser un entero entre 0 y 180"));
      return;
    }
  }

  const long requested = angleText.toInt();
  if (requested < AUX_SERVO_MIN_ANGLE || requested > AUX_SERVO_MAX_ANGLE) {
    Serial.println(F("ERROR SERVO: angulo fuera de rango 0-180"));
    return;
  }
  aux_servo_set_angle(static_cast<int>(requested));
  aux_servo_print_status();
}

#endif

#endif
