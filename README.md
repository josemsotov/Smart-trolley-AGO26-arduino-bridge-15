# Smart Trolley V14 — Arduino Bridge y ROS 2

Respaldo operativo del Smart Golf Trolley: firmware Arduino Mega 2560, puente ROS 2, fusión de encoders Hall/opto, follower y consola para operación en campo de golf.

## Acceso a la interfaz Fairway Trolley OS

Con el Raspberry Pi encendido y la PC en la misma red, abrir:

**http://192.168.40.74:8080/**

La portada debe mostrar **FAIRWAY TROLLEY OS**. Si aparece una versión anterior, usar `Ctrl+F5`.

- **Operación:** modo efectivo, GPS, odometría, Kinect, LiDAR, preparación, campo/hoyo y STOP.
- **Pruebas:** servicios, PWM/RPM/corriente, encoders, IMU/GPS, límites Stadia, Arduino y telemetría.
- **Entrenamiento:** postura/swing, seguimiento de pelota y estimación de distancia (funciones piloto).

Los datos del campo se guardan localmente en el navegador; la telemetría se recibe en tiempo real mediante `/ws`.

## Acceso al Raspberry Pi

```powershell
ssh josemsotov@192.168.40.74
```

Diagnóstico desde el Pi:

```bash
systemctl --user status robot-operator-web.service robot-follower.service
curl http://127.0.0.1:8080/api/state
```

Para reiniciar únicamente la consola web:

```bash
systemctl --user restart robot-operator-web.service
```

Código web del repositorio:

```text
simulation_ws/src/robot_operator_web/static/index.html
```

Copias desplegadas en el Pi:

```text
/home/josemsotov/robot_ws/src/robot_operator_web/static/index.html
/home/josemsotov/robot_ws/install/share/robot_operator_web/static/index.html
```

El reinicio del servicio web no sustituye el paro físico. Antes de una prueba de movimiento se debe verificar PWM/RPM en cero, trayectoria despejada y control manual disponible.

## Componentes principales

- `MOTOR-INTERFACE-V14.ino`: firmware principal.
- `Pins.h`: asignación de pines.
- `Hall_Sensors.h`: velocidad Hall y filtrado opto.
- `Motor_Control.h`: accionamiento y protecciones.
- `ROS2_Bridge.h`: protocolo serie Pi–Arduino.
- `simulation_ws/src/arduino_bridge_ros2/`: puente y fusión de encoders.
- `simulation_ws/src/robot_follower/`: follower y control ROS 2.
- `simulation_ws/src/robot_operator_web/`: servidor y consola web.
- `HANDOVER.md`: estado operativo y próximo paso.
- `GOLF_OPERATOR_UI_ANALYSIS.md`: capacidades y hardware recomendado.

## Hardware relevante

- Arduino Mega 2560 y Raspberry Pi con ROS 2 Jazzy.
- Optoencoders y Hall configurados a 45 PPR efectivos en el mismo eje.
- Diámetro nominal actual de rueda: 27 cm.
- Kinect RGB-D, LiDAR, MPU/IMU, GPS NEO-6M, Coral y Stadia.
- Enlace serie Arduino: 115200 baud.

## Fuente de verdad

Este repositorio es la línea de trabajo desde el respaldo del 24 de agosto de 2026. Consultar primero `HANDOVER.md` e `INDEX.md`. La carpeta `MOTOR-INTERFACE-V-13` es histórica y no debe editarse para cambios V14.
