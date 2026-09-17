# Suavizado en banco - 2026-09-10

Robot suspendido por confirmacion del usuario. IMU estatico: `hc off`,
balance `hb off`, PI `k off`. No valida trayectoria ni fuerza sobre suelo.

## Implementado

Firmware Mega: perfil seleccionable con motores parados:

- `k legacy`: modulacion anterior 0/25 PWM, periodo 100 ms (default al reiniciar).
- `k smooth`: periodo 20 ms; umbral configurable `k floor N` (1..25), default 18.
- Impulso inicial 25 PWM / 150 ms, PWM maximo 255 y watchdog conservados.
- Cambiar perfil/umbral durante movimiento se rechaza.

La primera variante continua (umbral 1) detuvo la rueda derecha a demanda
PWM 10, por lo que NO se recomienda. El umbral 18 conserva pulsos bajo ese
valor y salida continua por encima. No se ha validado como perfil de suelo.

Compilacion final: 66476 bytes flash, 6938 RAM (1254 libres; advertencia de
memoria baja). Carga y verificacion avrdude correctas.
Backup firmware original anterior a esta sesion:
`/home/josemsotov/robot_backups/smooth_20260910_HcgNYS/original.hex`.
La copia `smooth_20260910_rsTFws` contiene la primera variante experimental,
NO el firmware original.

## Metodo

`scripts/run_smooth_bench_pi.sh TAG off smooth 18` en Pi, junto con
`/tmp/ros_zenoh_test_env.sh` y `bench_smooth_20260910.py`.
Detiene temporalmente el stack principal, lanza puente aislado con watchdog
350 ms, comandos web a 10 Hz, limite 150 RPM, corta por telemetria vieja,
restaura stack al salir. Arduino conserva watchdog propio. Sin lidar/follower
en esta prueba: exclusivamente banco despejado. No usar este wrapper en suelo.

Cuatro segmentos de 7 s: avance .08 m/s, avance .22, reversa -.22,
giro .40 rad/s; rampa 1.5 s y cero final 1.5 s. Comparacion ventana 2.5..5.5 s.
Datos completos y resumen en `results/smooth_20260910/` y en Pi
`/home/josemsotov/robot_calibration/`.

Primera comparacion, desviacion estandar RPM reportada (L/R):

| Etapa | Anterior | 18 PWM / 20 ms |
|---|---:|---:|
| Avance lento | 3.27 / 2.85 | 1.38 / 2.23 |
| Avance | 4.85 / 4.76 | 4.38 / 3.83 |
| Reversa | 4.76 / 12.54 | 5.30 / 4.46 |
| Giro | 2.79 / 3.84 | 2.33 / 2.63 |

No mejora todas las metricas: reversa izquierda empeora ligeramente. Cambia
tambien la velocidad media a baja demanda, por lo que no es una comparacion
a velocidad igual ni una medicion directa de vibracion mecanica. Muestreo web
puede repetir telemetria y aliasar PWM; no permite medir cada pulso de 20 ms.
Hall/opto difieren 0..1 pulsos por rueda/ventana en estas dos capturas.

Repeticion del umbral 18: avance lento 1.06/1.33 RPM de desviacion, avance
4.72/4.58, reversa 5.63/6.04, giro 2.50/2.61. Confirma mejora a baja demanda
y giro en estas capturas, no mejora uniforme en reversa izquierda.
Al terminar se restaura el stack principal y se selecciona `k smooth` con
umbral 18 en runtime, manteniendo PI/heading apagados y motores parados.
Un reinicio Arduino vuelve a legacy.

## Pendiente

- Repetibilidad adicional y prueba Stadia en banco con observacion del usuario.
- Ajustar feedforward y PI: a .22 m/s se piden 15.6 RPM pero se observan ~65
  sin carga. NO afirmar control preciso de velocidad/posicion.
- Revisar filtro PI que pone a cero feedback > max(30, 3*target), y correccion
  cruzada Hall cuando PI esta apagado; pueden ocultar sobrevelocidad/oscilacion.
- Validar fuerza en suelo antes de cambiar el perfil de arranque permanente.
