# Smart Trolley Arduino Mega Shield - Bosquejo imprimible

Orientacion para imprimir y cablear:

- Vista desde arriba del shield.
- Arduino Mega colocado horizontalmente de derecha a izquierda.
- USB del Arduino queda al lado izquierdo.
- El shield va montado encima del Arduino.
- Los conectores de potencia/motores deben mirar hacia el borde trasero o externo del robot, no hacia el USB.

```text
                         BORDE SUPERIOR / LADO SENSORES
      +----------------------------------------------------------------------------+
      |                                                                            |
      |  J7 GPS                  J8 I2C 5V BUS                 J9 I2C 3V3 BUS      |
      |  +-----------+           +----------------+            +----------------+  |
      |  | 5V G TX RX|           | 5V G SDA SCL   |            |3V3 G SDA SCL   |  |
      |  |    D14 D15|           |    D20 D21     |            | TF/TOF via LV  |  |
      |  +-----------+           +----------------+            +----------------+  |
      |                                                                            |
      |                         +------------------------+                         |
      |                         |  LEVEL SHIFTER I2C     |                         |
      |                         |  HV=5V  LV=3V3         |                         |
      |                         |  HV1=SDA20 LV1=SDA_TF  |                         |
      |                         |  HV2=SCL21 LV2=SCL_TF  |                         |
      |                         +------------------------+                         |
      |                                                                            |
      |  J5 HALL/OPTO LEFT       TEST POINTS / LEDS          J6 HALL/OPTO RIGHT   |
      |  +---------------+       +--------------------+      +---------------+     |
      |  |5V G HALL OPTO |       | 5V 3V3 G SDA SCL   |      |5V G HALL OPTO |     |
      |  |   D19   D3    |       | PWM_L PWM_R STOPs  |      |   D18   D2    |     |
      |  +---------------+       +--------------------+      +---------------+     |
      |                                                                            |
      |                                                                            |
USB   |====================== ARDUINO MEGA HEADERS BELOW =======================|  |
<-----|                                                                            |
LADO  |                                                                            |
IZQ   |  J1 MOTOR LEFT CONTROL                         J2 MOTOR RIGHT CONTROL     |
      |  +--------------------------+                  +-------------------------+ |
      |  |G  5V  PWM DIR BRK STP    |                  |G  5V  PWM DIR BRK STP   | |
      |  |      D46 D52 D50 D48     |                  |      D44 D30 D28 D26    | |
      |  +--------------------------+                  +-------------------------+ |
      |                                                                            |
      |  J3 CURRENT LEFT                             J4 CURRENT RIGHT              |
      |  +-------------+                            +-------------+                |
      |  |5V G OUT=A4  |                            |5V G OUT=A3  |                |
      |  +-------------+                            +-------------+                |
      |                                                                            |
      |  +----------------------+                  +----------------------+        |
      |  | MOTOR LEFT POWER     |                  | MOTOR RIGHT POWER    |        |
      |  | hacia driver izq     |                  | hacia driver der     |        |
      |  +----------------------+                  +----------------------+        |
      |                                                                            |
      +----------------------------------------------------------------------------+
                         BORDE INFERIOR / LADO DRIVERS-MOTORES
```

## Conectores recomendados

Usa conectores bloqueados o con seguro si es posible. Para senales pequenas JST-XH funciona bien; para potencia usa bornera, XT, Molex Mini-Fit, o similar.

| Ref | Bloque | Pines sugeridos | Senales |
|---|---|---:|---|
| J1 | Control driver motor izquierdo | 6 | GND, 5V, PWM_L D46, DIR_L D52, BRAKE_L D50, STOP_L D48 |
| J2 | Control driver motor derecho | 6 | GND, 5V, PWM_R D44, DIR_R D30, BRAKE_R D28, STOP_R D26 |
| J3 | ACS712 izquierdo | 3 | 5V, GND, OUT A4 |
| J4 | ACS712 derecho | 3 | 5V, GND, OUT A3 |
| J5 | Sensores rueda izquierda | 4 | 5V, GND, HALL_L D19, OPTO_L D3 |
| J6 | Sensores rueda derecha | 4 | 5V, GND, HALL_R D18, OPTO_R D2 |
| J7 | GPS Serial3 | 4 | 5V, GND, Arduino TX3 D14, Arduino RX3 D15 |
| J8 | I2C lado Arduino/MPU | 4 | 5V, GND, SDA D20, SCL D21 |
| J9 | I2C lado 3.3V TF-Luna/ToF | 4 o 5 | 3V3, GND, SDA_3V3, SCL_3V3, optional TF_MODE_GND |

## Distribucion fisica recomendada

1. Mantener J1 y J2 abajo, cerca del lado de drivers/motores.
2. Mantener J5 y J6 hacia los laterales para que cada rueda entre por su lado.
3. Mantener J7 GPS arriba/izquierda o arriba/centro, lejos de cables PWM de motor.
4. Mantener J8/J9 arriba, lejos de potencia, con trazas SDA/SCL cortas.
5. Poner el level shifter entre J8 y J9, visible y etiquetado HV/LV.
6. Poner test points en una fila central para diagnostico rapido con multimetro/osciloscopio.

## Notas electricas criticas

- No pasar corriente de motor por el shield si no es necesario. El shield debe llevar control/senal; la potencia de motor debe ir por cableado grueso externo.
- Todos los GND deben estar comunes, pero las rutas de retorno de motor deben evitar pasar debajo del I2C.
- D20/D21 del Mega tienen pullups hacia el lado 5V/3.9V observado; el TF-Luna necesita lado 3.3V mediante level shifter.
- Pin 5 del TF-Luna debe ir a GND antes de energizar el sensor para seleccionar modo I2C.
- Dejar pin 6 del TF-Luna sin conectar salvo que se implemente modo ready/trigger dedicado.
- Agregar serigrafia grande: LEFT, RIGHT, PWM, DIR, BRK, STP, 5V, GND, SDA, SCL.

## Pinout usado por firmware actual

| Funcion | Pin Arduino Mega |
|---|---:|
| PWM motor izquierdo | D46 |
| DIR motor izquierdo | D52 |
| BRAKE motor izquierdo | D50 |
| STOP motor izquierdo | D48 |
| PWM motor derecho | D44 |
| DIR motor derecho | D30 |
| BRAKE motor derecho | D28 |
| STOP motor derecho | D26 |
| Hall izquierdo | D19 |
| Hall derecho | D18 |
| Opto izquierdo | D3 |
| Opto derecho | D2 |
| I2C SDA | D20 |
| I2C SCL | D21 |
| GPS TX3 | D14 |
| GPS RX3 | D15 |
| Corriente izquierda ACS712 | A4 |
| Corriente derecha ACS712 | A3 |

## Checklist antes de fabricar

- Confirmar orientacion real del Arduino montado en el robot con USB a la izquierda.
- Confirmar si los conectores de motores deben salir hacia abajo, hacia atras o hacia laterales.
- Confirmar tipo exacto de conector para drivers ZS-X11H.
- Confirmar si 3.3V vendra del Mega o de regulador dedicado del shield.
- Confirmar corriente total de sensores 5V para no sobrecargar el Mega.
- Confirmar si se quieren dos conectores TF-Luna separados en J9A/J9B.
