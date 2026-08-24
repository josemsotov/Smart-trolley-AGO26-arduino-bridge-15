# Fairway Trolley OS — análisis de interfaz y capacidades

Fecha: 2026-08-23

## Objetivo

Separar la experiencia de usuario en tres contextos con distinto nivel de riesgo:

1. **Operación:** conducir, seguir al jugador, comprender el entorno y detener el robot.
2. **Pruebas:** diagnosticar servicios, sensores, motores y estimadores sin contaminar la vista de campo.
3. **Entrenamiento:** desarrollar funciones deportivas de forma incremental y sin prometer métricas que el hardware actual no puede medir.

## Datos disponibles hoy

| Subsistema | Datos disponibles | Uso operativo |
|---|---|---|
| Arduino / motores | PWM, RPM, dirección, corriente, comando lineal/angular | Confirmar ejecución, bloqueo, sobrecarga y asimetría |
| Hall 45 PPR + opto 60 PPR | Conteos crudos, fusión y odometría | Velocidad, distancia y diagnóstico redundante; Hall es referencia primaria actual |
| MPU9250/6500 | aceleración, giro, yaw y pitch | Orientación, estabilidad y fusión de odometría del robot |
| NEO-6M | fix, satélites, HDOP y salud serial | Ubicación general y disponibilidad de navegación exterior |
| LiDAR 2D | nube polar, distancia frontal y grupos | Obstáculos y asociación de persona en el plano del sensor |
| Kinect RGB-D | RGB, profundidad, cuerpo, rostro y gesto | Identidad, postura, distancia cercana y seguimiento humano |
| Coral TPU | estado e inferencia de persona | Aceleración de modelos específicamente entrenados |
| Stadia | conexión, modo, neutral y takeover | Control manual y parada de seguridad del follower |
| ROS2 supervisor | modo solicitado/efectivo, razón y readiness | Explicar por qué el robot se mueve o permanece detenido |

## Qué debe mostrar Operación

- STOP permanente y visualmente dominante.
- Modo efectivo y razón, no solo el botón solicitado.
- Conexión del Stadia y disponibilidad del takeover.
- Frescura de Arduino, LiDAR, RGB, profundidad, follower, GPS y odometría.
- Objetivo del follower, distancia frontal, comandos y movimiento real.
- Campo, hoyo, par, yardas y notas operativas.
- GPS con fix/satélites/HDOP; un mapa se añadirá cuando se publiquen latitud y longitud.
- Alertas accionables, evitando registros seriales en la vista principal.

## Qué debe mostrar Pruebas

- Estado por subsistema y edad del último dato.
- PWM/RPM/corriente por rueda y conteos de los cuatro encoders.
- Estado de fusión Hall/opto y discrepancia por rueda.
- IMU, GPS y LiDAR con valores crudos relevantes.
- Límites temporales de Stadia.
- Comando Arduino de una línea, aislado como control avanzado.
- Resultados de pruebas con timestamp, configuración, criterio de éxito y posibilidad de exportar.

## Qué debe mostrar Entrenamiento

### Viable con el hardware actual

- Postura inicial, alineación de hombros/cadera, estabilidad y balance aproximado.
- Secuencia corporal lenta: address, backswing y finish.
- Tempo general del cuerpo, con precisión limitada por 30 fps.
- Putting o bola rodada en una zona controlada, después de entrenar un detector y calibrar el plano.

### Experimental

- Identificación del palo por visión.
- Trayectoria aproximada del palo a baja velocidad.
- Detección de bola cercana con Coral y una cámara mejor ubicada.
- Estimación de distancia corta mediante profundidad calibrada.

### No confiable con los sensores actuales

- Instante exacto de impacto.
- Velocidad de cabeza del palo y velocidad inicial de bola.
- Spin, launch angle y carry de un golpe completo.
- Seguimiento de bola en vuelo con Kinect o LiDAR 2D.
- Distancia de golpe precisa con GPS NEO-6M.

## Recomendación de cámara

Para análisis de swing e impacto, añadir una cámara con:

- global shutter;
- 120 fps como mínimo, preferiblemente 240 fps;
- exposición manual y obturador corto;
- 1080p si se analizará cuerpo completo, o ROI de alta velocidad;
- montaje lateral fijo y calibrado;
- iluminación suficiente para evitar motion blur.

Para bola en vuelo, una sola cámara de 120 fps normalmente no basta. Las opciones, en orden de robustez, son:

1. radar Doppler / launch monitor;
2. par estéreo de cámaras global-shutter sincronizadas;
3. cámara de alta velocidad con zona de vuelo muy controlada;
4. RTK GNSS o telémetro láser para validar distancia final, no para observar el vuelo.

## Arquitectura recomendada

- Mantener el Pi enfocado en seguridad, control y adquisición ROS2.
- Ejecutar análisis pesado de swing/bola en esta PC o en un módulo dedicado.
- Publicar resultados como tópicos ROS2 separados (`/golf/swing/state`, `/golf/ball/track`, `/golf/session`).
- Guardar sesiones en un formato reproducible: video, timestamps, calibración, métricas y versión del modelo.
- No permitir que una función de entrenamiento publique directamente en `/cmd_vel`.

## Estado de implementación

- Nueva interfaz local implementada en `simulation_ws/src/robot_operator_web/static/index.html`.
- Tres áreas: Operación, Pruebas y Entrenamiento.
- Datos del campo persistentes en el navegador.
- Salud de servicios derivada de frescura real de tópicos.
- Validación visual local completada.
- Despliegue al Pi pendiente: `192.168.40.74` no respondió por SSH durante la entrega.