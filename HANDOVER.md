# Handover — Smart Trolley V14

Actualizado: 2026-10-05

## 2026-10-06 - Apagado seguro desde Fairway Trolley OS

- La barra superior incorpora `APAGAR PI` con confirmación explícita.
- El backend exige `confirm=POWEROFF`, ordena IDLE, EMERGENCY_STOP y velocidad
  cero, espera la parada, valida autorización con `systemctl poweroff --dry-run`
  y programa el apagado un segundo después de responder al navegador.
- El botón queda deshabilitado durante la secuencia y muestra el estado
  `PI APAGÁNDOSE`; un fallo de autorización se presenta al operador.

## 2026-10-05 - Servo auxiliar desde Stadia

- Servo independiente conectado con señal al pin 38 del Arduino Mega,
  confirmado mediante prueba física secuencial de los pines 34/36/38.
- El botón Y conserva su secuencia segura (modo Stadia, balance desactivado y
  STOP) y después envía `SERVO TOGGLE`. El SG90/MG90S fue sustituido por un
  MG996R. La medición mediante la ruta real del botón Y dio unos 95–100°
  físicos con 0/154; el ajuste fino final quedó en 0/142 para buscar 90°.
- El firmware acepta además `SERVO <0-180>` y `SERVO STATUS`.
- `Servo_Control.h` usa Timer1 directamente. No usar `Servo.h`: en Mega puede
  tomar Timer5, reservado por los motores de tracción en los pines 44/46.
- El servo debe alimentarse con una fuente de 5–6 V adecuada para su corriente,
  con masa común entre esa fuente y el Arduino; no alimentar un servo de carga
  desde el pin 5 V del Mega.
- Configuración fuente posterior: `AUX_SERVO_MODEL_SG90` queda seleccionada por
  defecto con toggle 0/180. `AUX_SERVO_MODEL_MG996R` queda disponible como
  alternativa con la calibración confirmada 0/142; solo puede activarse un
  modelo. Tras reinstalar físicamente el SG90, el firmware activo volvió a la
  configuración SG90 predeterminada 0/180.
- Reensamblaje SG90: 2000 us coincide con el tope mecánico definido como 90°,
  mientras 1000 us dejaba el extremo opuesto a unos 45°. La prueba a 500 us
  alcanzó el tope opuesto y produjo zumbido; se desconectó inmediatamente y se
  restauró el arranque seguro a 1000 us. `SERVO PULSE <500-2500>` permite
  buscar el extremo gradualmente. La opción MG996R conserva 1000–2000 us.
- El SG90 presentó un zumbido leve incluso con trims 1020/1040 us una vez
  instalado el horn. Como el mecanismo no necesita fuerza de retención, el
  firmware libera automáticamente la señal 1 s después de cada movimiento;
  la siguiente orden vuelve a adjuntar pin 38 antes de mover.
- El movimiento instantáneo se sustituyó por una rampa no bloqueante. La prueba
  1000–2125 us alcanzó unos 87° pero conservó pequeños tirones; el ajuste fino
  quedó en 1000–2165 us. La rampa 2 us/20 ms resultó demasiado lenta; el ajuste
  perfil 2 us/5 ms tardó unos 5 s reales; el ajuste final es 3 us cada 5 ms,
  estimado en unos 3.3 s reales para el recorrido completo.

## 2026-10-05 - Cámara ELP global-shutter para análisis de swing

- Cámara identificada como USB `32e4:0234` y configurada por la ruta persistente
  `/dev/v4l/by-id/usb-Global_Shutter_Camera_Global_Shutter_Camera_01.00.00-video-index0`.
- La ELP está conectada directamente al puerto USB de la Pi `4-2`. El Arduino
  Mega se trasladó al hub y conserva su ruta persistente `/dev/serial/by-id/...`.
- El puerto anteriormente ocupado por el LiDAR inferior se reasignó a la ELP.
  `enable_lidar_lower` queda desactivado por defecto; `/scan_lower` no se espera
  en la configuración física actual. El LiDAR superior continúa fresco y activo.
- Fairway Trolley OS incorpora estado y controles independientes para la ELP.
  Cada captura se limita a 15 s, exige al menos 700 MB libres y usa un único
  proceso de grabación. Se conserva un maestro MKV MJPEG a 1920x1080/90 FPS y
  se genera un proxy MP4 H.264 a 960x540/90 FPS para reproducción web.
- La pestaña ENTRENAMIENTO muestra un feed ELP MJPEG de 640x480/30 FPS para
  encuadre. El backend mantiene una sola apertura de preview, la detiene y
  libera antes de grabar a 1080p/90 FPS, y la reanuda durante la generación del
  proxy. Validación real del traspaso: preview activo, pausado durante captura,
  194 fotogramas a 90.0 FPS en 2.156 s y preview activo nuevamente.
- Prueba corta real: 290 fotogramas, 3.222 s, 90.0 FPS, maestro de 51.5 MB y
  proxy de 2.98 MB. Prueba automática al límite: 1,351 fotogramas, 15.011 s,
  90.0 FPS y maestro de 222.4 MB. El proxy apareció en la biblioteca con
  `source=elp`; el maestro quedó enlazado en los metadatos. El conteo exhaustivo
  del maestro usa un timeout específico de 45 s, mientras las sondas normales
  conservan 15 s. Kinect, LiDAR superior y Arduino permanecieron frescos; PWM
  y RPM se mantuvieron en 0/0.
- Home Assistant sigue usando la interfaz canónica mediante
  `http://192.168.40.74:8080/?v=elp-live-20261005`.
- Respaldos previos:
  `/home/josemsotov/robot_backups/elp_camera_20261005_175131` y
  `/home/josemsotov/robot_backups/elp_live_preview_20261005_181737`.
  Respaldos Home Assistant:
  `%LOCALAPPDATA%\SmartTrolley\ha-backups\smart-trolley-20261005-175948.json`
  y `smart-trolley-20261005-181849.json`.
- Próxima fase: ajustar exposición y ganancia manuales con iluminación real,
  validar 10–15 s sostenidos y desarrollar extracción de rasgos del palo/cuerpo.
  La ELP a 90 FPS no acredita velocidad de bola, distancia ni función de seguridad.

## 2026-10-05 - Interfaz canónica y restauración del stack

- Navegador, Home Assistant y pantalla táctil usan la misma portada responsiva
  de Fairway Trolley OS en `http://192.168.40.74:8080/`.
- El acceso histórico `/static/touch.html` redirige a la portada canónica para
  evitar que las funciones diverjan entre plataformas.
- La barra superior incluye `RESTAURAR STACK`. La acción exige confirmación,
  ordena STOP/IDLE, espera la parada y programa mediante systemd el reinicio de
  `robot-follower.service` y `robot-operator-web.service`.
- Home Assistant usa la versión de caché
  `?v=unified-interface-20261005`.
- Copia previa en la Pi:
  `/home/josemsotov/robot_backups/canonical_interface_20261005_105416`.
- Copia previa de Home Assistant:
  `%LOCALAPPDATA%\SmartTrolley\ha-backups\smart-trolley-20261005-105506.json`.
- Validación funcional: restauración real programada, ambos servicios regresaron
  a `active`, la portada respondió HTTP 200 y el modo final fue `IDLE`.

### Recuperación Kinect tras pérdida de alimentación

- El Kinect dejó de publicar porque la batería principal agotada no alimentaba
  el adaptador del sensor. USB conservó únicamente el motor `045e:02b0`; cámara
  `045e:02ae` y audio `045e:02ad` estaban ausentes, y `kinect_node` notificaba
  `Invalid index [0]`.
- Tras restaurar alimentación aparecieron las tres interfaces USB. Un reinicio
  de `robot-follower.service` recuperó RGB a 20.5 FPS y profundidad fresca
  (0.633 s). La demanda, PWM y RPM permanecieron en cero durante el diagnóstico.
- Ante el mismo síntoma, comprobar batería/alimentación y las tres interfaces
  USB antes de reiniciar servicios o modificar software.

## 2026-10-02 - Interfaz unificada con Home Assistant

- Fairway Trolley OS sigue siendo la unica interfaz canonica en
  `http://192.168.40.74:8080/`.
- El dashboard `smart-trolley` de Home Assistant usa estrategia iframe y apunta
  a esa interfaz completa con version de cache
  `?v=unified-interface-20261002`; no mantiene una segunda implementacion.
- Se desplego la pestana `VISUAL AID` con la imagen Stadia suministrada y la
  leyenda de controles en las rutas source/install del Pi.
- Respaldo previo del dashboard HA en
  `%LOCALAPPDATA%\SmartTrolley\ha-backups\smart-trolley-20261002-183049.json`.
- Respaldo previo de la web del Pi en
  `/home/josemsotov/robot_backups/visual_aid_20261002_181451`.

## 2026-09-17 - Kinect recuperado y sincronizacion Escritorio

- Tras reconexion USB Kinect estaba enumerado pero sin captura reciente.
  Reinicio autorizado de robot-follower.service de usuario recupero RGB
  a 25.9 FPS y profundidad fresca (0.653 s); ambos LiDAR frescos y motores
  PWM/RPM cero. No se cambio firmware en esta recuperacion.
- Copia del proyecto en Escritorio:
  `C:\Users\cools\Desktop\Smart-trolley-AGO26-arduino-bridge-15`.
- Respaldo/sincronizacion solicitado: codigo, firmware, documentacion,
  resultados de pruebas y respaldos HEX se incluyen en GitHub y en la copia
  del Escritorio. Entornos virtuales, credenciales y salidas generadas siguen
  excluidos de Git segun `.gitignore`.
- Las dos carpetas son clones independientes: cambios futuros requieren
  commit/push/pull; no existe sincronizacion automatica entre carpetas.

## 2026-09-16 - Segundo LD19 e interfaz

- Superior USB by-path puerto 1.3, inferior 1.4: ambos CP2102 tienen serie
  0001; no usar by-id compartido. Mantener y etiquetar puertos/cables.
- Ambos activos a 10 Hz: `/scan` / `base_laser` y `/scan_lower` /
  `base_laser_lower`. Inferior a z=0.15 m, roll=pi (invertido, flecha adelante).
  x=-0.10/y=0 provisionales hasta medir posicion horizontal.
- Panel inferior en Operacion, estado en Operacion/Pruebas de
  `http://192.168.40.74:8080/`. Datos frescos confirmados por API; canvas y JS
  servidos correctamente. Correccion de izquierda/derecha y frente 0/2pi.
- Inferior NO incorporado aun al frenado ni SLAM. Retornos cercanos de 2.5 cm:
  revisar objetos/montaje antes de usarlo para seguridad. No se movieron motores.
- Detalles, respaldos y pruebas: `simulation_ws/DUAL_LIDAR_INTEGRATION.md`.

## 2026-09-13 - Pausa obstaculos; soporte TF-Luna local

Usuario solicita pausar la prueba motorizada de obstaculos para integrar TF-Luna.
Driver I2C TF_Luna.h implementado, dos canales0x10/0x11 desactivados al boot,
comandos tf status/on/off, trigger sin delay, identidad/calidad/frescura y timeout.
Compilado y probado con Wire simulado; NO cargado al Arduino, NO desplegado al Pi.
68780 flash /7125 RAM (1067 libres). Cableado mediante adaptador3.3V pendiente.
Guia y limitaciones: TF_LUNA_INTEGRATION.md. No se integra aun a frenado/UI.

## 2026-09-11 - Encoder izquierdo, comparacion de filtro

Prueba manual: Hall453/opto454 para diez vueltas indicadas. Con movimiento
a demanda15 aparece deficit opto ~5-7%; demanda20/25 concordo en una prueba.
Selector de diagnostico `j leftscale 50..100` instalado, default100.
Comparacion100 vs80 NO mejoro; restaurado100. No asumir ruido opto como causa
unica ni cambiar PPR. Detalles: simulation_ws/results/manual_encoder/filter_ab_20260911.md.

## Banco: suavizado 2026-09-10

Firmware cargado y verificado con perfiles `k smooth` / `k legacy` y umbral
`k floor 18`. Ensayos automaticos avance/reversa/giro completos, incluyendo
repeticion. Detalles, limitaciones, respaldo original y resultados en
`simulation_ws/SMOOTH_BENCH_20260910.md`. Perfil legacy sigue siendo default
tras reiniciar Arduino; smooth queda habilitado solo en runtime para banco.
PI y heading apagados. No extrapolar a suelo ni afirmar velocidad calibrada.

## Actualizacion 2026-08-25 - PPR efectivo de optoencoders

- Las barridas repetidas PWM 25-80 mostraron una relacion estable cercana a 1:1 entre Hall y opto en ambas ruedas.
- Se adopta `45 PPR` efectivos para los optoencoders, igual que los Hall; el supuesto anterior de 60 PPR queda retirado.
- Firmware `PPR_OPTO_ENCODERS`, puente ROS 2, fusion, launch files, perfil de hardware, calibradores y documentacion fueron alineados a 45 PPR.
- Diametro fisico de rueda permanece en `0.27 m`; no se modifica para compensar la escala del encoder.
- PWM 90 sigue excluido por la caida anomala de conteos Hall. Para pruebas operativas se conserva el rango prudente PWM 25-40.
- La rueda izquierda mostro arranque intermitente en PWM 10-20; no usar ese rango para caracterizacion de posicion.

## Actualizacion 2026-08-25 - lazo cerrado Hall/opto

- Odometria ROS 2 fusiona Hall y opto 50/50 con discrepancia <=5%, usa 75/25 a 5-12% y vuelve a Hall por encima de 12%.
- PI interno de velocidad usa RPM Hall/opto promediada solo cuando ambos sensores concuerdan dentro de 12%; ante ausencia, reset o ruido opto vuelve a Hall.
- Una señal opto aislada nunca genera movimiento ni realimentacion valida.
- Telemetria del firmware agrega `Lfrpm/Rfrpm` y fuente `Lfs/Rfs` (`F` fusionada, `H` Hall/fallback).
- PWM 90 permanece fuera del rango de control por discrepancia severa y simetrica entre Hall y opto.
- Firmware de fusion instalado y verificado por `avrdude` (65696 bytes); respaldo previo en `/home/josemsotov/robot_backups/pre_fused_loop_20260825.hex`.
- Prueba estatica aprobada: PI activo, telemetria `Lfrpm/Rfrpm` y fallback `Lfs/Rfs` operativos, parada final PWM/RPM cero.
- Prueba dinamica pendiente de repetir: con PWM comandado 20-30 los motores no vencieron movimiento; verificacion directa `q 30` dio L Hall/opto 1/0 y R 11/25, muy por debajo de la barrida anterior. Revisar potencia/habilitacion/arnes antes de ajustar ganancias.


## Actualizacion 2026-08-20 - plataforma de movimiento y odometria

- Workspace local activo migrado a `D:\1-EXTERNAL\PROYECTOS JMS 2025\SMART-TROLLEY-JUN-2026\MOTOR-INTERFACE-V14`.
- Raspberry Pi accesible en `josemsotov@192.168.40.74`.
- Zenoh persistente y servicios `smart-trolley-zenoh-router`, `robot-follower` y `robot-operator-web` activos.
- Diametro fisico real: `wheel_dia=0.27 m`; Pi recompilado y parametro activo verificado.
- Optoencoders configurados a `ppr=45` efectivos: D3 izquierdo y D2 derecho. El comando `e` publica optos; Hall permanece como referencia primaria de RPM/odometria.
- IMU activa con fusion inicial yaw/gyro Z. GPS comunica, pero la ultima verificacion seguia sin fix ni satelites.
- Prueba terrestre util: inicio `L=1794 R=2225`, final `L=1988 R=2345`, distancia fisica `30.3 cm`; deltas `L=194 R=120`.
- Hay asimetria significativa entre encoders. La calibracion de odometria no esta cerrada.
- El Pi tuvo perdidas temporales de SSH, sin reinicio ni bajo voltaje (`get_throttled=0x0`); revisar Wi-Fi.
- Estado seguro al cierre: servicios activos, `/cmd_vel=0`, robot en `PAUSE`.

### Siguiente paso recomendado

1. Repetir dos recorridos terrestres rectos y medidos con Stadia.
2. Registrar conteos iniciales/finales por rueda y distancia fisica.
3. Evaluar factores de escala separados izquierda/derecha.
4. Conservar el diametro fisico `0.27 m`; no usarlo para ocultar asimetrias de encoder.
5. Validar avance, retroceso y parada antes de navegacion autonoma.
## Estado de cierre

- Raspberry Pi 5 de 8 GB: `josemsotov@192.168.40.73`.
- Interfaz: `http://192.168.40.73:8080`.
- Servicios activos:
  - `robot-follower.service`
  - `robot-operator-web.service`
- Estado seguro verificado:
  - modo `STADIA`
  - follower deshabilitado
  - `/cmd_vel = 0 / 0`
  - PWM `0/0`
  - RPM `0/0`
- No se realizó ninguna prueba con movimiento real.
- Mantener el robot suspendido para las próximas pruebas.

## Safety net vigente

- Stadia es el modo predeterminado y toma control al conectarse por Bluetooth.
- El mando exige palancas centradas antes de armarse.
- Solo `/follower/authorized_enable` puede habilitar intencionalmente FOLLOWER.
- Stadia, OFF, desconexión y STOP cancelan autorizaciones anteriores.
- El follower exige una sesión facial válida para arrancar.
- Watchdog Arduino: `cmd_timeout=0.5`.
- Paro reproducible:
  `.codex_runtime_fix/pi8_safety_net/emergency_stadia_stop.sh`.

## Cambios desplegados el 2026-07-24

En `follower_node.py` y `follower_params.yaml`:

- Agrupación de puntos LiDAR contiguos y selección por alineación visual,
  continuidad de distancia y tamaño.
- Telemetría de distancia/ángulo crudos, cantidad de clústeres y estado.
- Procesamiento body–LiDAR disponible en `FACE_STATIC_DRY_RUN`, siempre con salida cero.
- Sin body track fresco:
  - estado `no_person_track`
  - STOP
  - no se crea un objetivo nuevo.
- Un objetivo inicial exige rostro visible, sesión válida e identidad verificada.
- Cada enrolamiento reinicia completamente la referencia LiDAR heredada.
- Se conserva la última referencia durante pérdidas visuales breves.
- Compuerta de distancia facial:
  - escala inicial `face_distance_scale_m=0.185`
  - margen `lidar_face_distance_gate_m=0.45`
  - timeout `1.50 s`
  - estado de rechazo `face_distance_mismatch`.
- Compensación de montaje cámara–LiDAR:
  - `lidar_camera_yaw_deg=90.0`
  - ángulos normalizados a `[-π, π]`.
- Política final de continuidad:
  - cambios mayores de `0.25 m` durante la misma sesión se rechazan
  - estado `distance_discontinuity`
  - STOP y conservación de la última distancia válida
  - ya no se acepta otro objeto después de varios barridos.

## Resultados observados

### Aprobado

- Rostro frontal:
  - `face_x=0.526–0.532`
  - identidad verificada.
- Body track aproximadamente `0.94`.
- Después de compensar `90°`, adquisición corporal estable:
  - distancia `1.23–1.29 m`
  - clúster `16–22` puntos
  - ángulo aproximado `0.05 rad`.
- En todas las muestras:
  - `/cmd_vel=0`
  - PWM/RPM en cero.

### Falló de forma segura

- En la prueba lateral, al salir parcialmente del cuadro el selector migró desde
  `≈1.27 m` hacia un objeto de `≈0.72–0.76 m`.
- La sesión facial y el body track se perdieron temporalmente.
- No hubo movimiento porque el modo era dry-run.
- La causa fue la política anterior que aceptaba una discontinuidad después de tres
  barridos consistentes.
- Esa política fue eliminada y sustituida por rechazo estricto de cambios `>0.25 m`.

### Pendiente de validar

La nueva política `distance_discontinuity` fue desplegada, compilada y el servicio quedó
activo, pero todavía no se repitió la adquisición central ni la prueba lateral después
de este último cambio.

## Reanudación recomendada

1. Confirmar robot suspendido y paro físico accesible.
2. Abrir `http://192.168.40.73:8080`.
3. Colocarse a aproximadamente `1.3 m`, torso centrado y rostro mirando al lente.
4. Iniciar `FACE_STATIC_ENROLL`.
5. Aprobar adquisición central solo si:
   - identidad y sesión válidas
   - body track fresco
   - LiDAR `≈1.2–1.4 m`
   - clúster corporal consistente
   - `/cmd_vel`, PWM y RPM en cero.
6. Repetir desplazamiento lateral en dry-run.
7. Confirmar que un objeto a `≈0.72 m` produzca `distance_discontinuity` y que la
   referencia corporal no cambie.
8. Regresar al centro y confirmar recuperación a `≈1.2–1.4 m`.
9. Solo después evaluar una prueba muy limitada con ruedas suspendidas.
10. No apoyar las ruedas hasta validar STOP, pérdida de persona y takeover de Stadia.

## Fuente activa respaldada

- `.codex_runtime_fix/pi8_safety_net/current/follower_node.py`
- `.codex_runtime_fix/pi8_safety_net/current/follower_params.yaml`
- `.codex_runtime_fix/pi8_safety_net/current/stadia_node.py`
- `.codex_runtime_fix/pi8_safety_net/current/arduino_node.py`
- `.codex_runtime_fix/pi8_safety_net/web_current/`

Las capturas de cámara y cachés Python permanecen excluidas de GitHub.

## Comandos útiles

```text
ssh josemsotov@192.168.40.73
systemctl --user status robot-follower.service robot-operator-web.service
```

## 2026-08-21 - Perfil ampliado Hall/opto (banco suspendido)

- `MAX_PWM_VALUE` operativo permanece en 40 para ROS2/Stadia.
- El comando diagnostico `q <L|R> <pwm>` tiene limite independiente `DIAGNOSTIC_MAX_PWM = 80`.
- Firmware compilado (59990 bytes), respaldado en Pi como `/home/josemsotov/robot_backups/pre_20260821_diag_pwm80.hex`, cargado y verificado con avrdude.
- Matriz historica: PWM 10,15,20,25,30,35,40,50,60,70,80; 3 repeticiones por rueda; originalmente evaluada bajo el supuesto Hall 45 PPR contra opto 60 PPR, reemplazado por 45/45 tras las pruebas del 2026-08-25.
- Zona mas consistente: PWM 25-40 (aprox. -3.4% a +5.4% de error medio, excepto dispersion puntual izquierda a 40).
- PWM 10-15: sobreconteo fuerte; PWM 50-80: subconteo creciente, alrededor de -20% a -23% desde PWM 60.
- Informes: `encoder_calibration_reports/encoder_cross_extended_20260821.{json,csv}`.
- Al terminar: `robot-follower.service` activo, `/motor_status` Lpwm=0 Rpwm=0 Lrpm=0 Rrpm=0.
## 2026-08-21 - Filtro opto adaptativo V3 validado

- Mejora 1: limites adaptativos ampliados de L=5500/R=6000..15000 us a L=2500/R=2500..40000 us.
- Mejora 2 evaluada: ganancia izquierda por bandas; corrigio extremos pero sobrefiltro PWM 15-20.
- Mejora 3 activa: ganancia izquierda por intervalo Hall: >=50000 us:650 permille; >=27000:500; >=12000:450; >=8000:375; menor:350. Derecha conserva 520 permille.
- Comparacion misma matriz (PWM 10..80, 3 repeticiones/rueda): baseline MAE 18.23%, V1 6.00%, V2 4.13%, V3 3.14%.
- Peor muestra: baseline 118.75%; V3 10.71%.
- Informes JSON/CSV en `encoder_calibration_reports/` para baseline, adaptive_bounds_v1, left_piecewise_v2 y left_piecewise_v3.
- `MAX_PWM_VALUE` operativo sigue en 40; `DIAGNOSTIC_MAX_PWM` sigue en 80.
- Estado final: follower y Zenoh activos; motor_status Lpwm=0 Rpwm=0 Lrpm=0 Rrpm=0.
## 2026-08-21 - Base de lazo cerrado: fusion Hall/opto

- Firmware `e` extendido: `e <optoL> <optoR> <hallL> <hallR>`; conteos acumulados tomados atomicamente.
- ROS2 incorpora `WheelEncoderFusion` con ventana de 10 muestras (~0.5 s): <=5% usa OPTO; 5-12% BLEND; >12% fallback HALL; PWM=0 fuerza STOP y delta cero.
- Nuevo topico `/encoder_fusion/status`; `/encoder_counts` incluye fusion y los cuatro conteos crudos.
- Covarianza de `/odom` aumenta automaticamente cuando baja la confianza.
- Compatibilidad preservada con trama antigua `e <L> <R>`.
- Pruebas unitarias directas: OPTO, BLEND, HALL fallback y STOP aprobadas. Firmware 60184 bytes, verificado por avrdude.
- Respaldo firmware: `/home/josemsotov/robot_backups/pre_20260821_dual_encoder_fusion.hex`.
- Respaldo nodo Pi: `arduino_node.py.pre_encoder_fusion_20260821.bak`.
- Validacion estatica: follower activo; fusion L/R=STOP conf=1.00; odom linear/angular=0; motor PWM/RPM=0.
- Observacion: OL acumulo flancos crudos con PWM=0; fueron rechazados completamente por la fusion/guardia de reposo.
- Pendiente antes de ajustar PID: prueba dinamica controlada para observar transiciones OPTO/BLEND/HALL y confirmar si el robot esta suspendido o en suelo.
### Prueba dinamica suspendida de fusion

- Escalones comandados: 0.08, 0.15 y 0.25 m/s, 3 s cada uno, con parada entre escalones.
- El puente se ejecuto aislado temporalmente para evitar ceros del `cmd_vel_mux`; el servicio completo fue restaurado automaticamente.
- Se observaron correctamente los estados OPTO, BLEND y HALL. Ante discrepancia del opto izquierdo, la odometria uso Hall como fallback.
- Resultado acumulado fusionado de la corrida: L=239.000, R=234.833 pulsos equivalentes; conteos crudos finales OL=601 OR=262 HL=199 HR=204 (incluyen acumulados previos al inicio).
- La seleccion cambia durante transitorios; para el primer ajuste de velocidad usar PI (D=0) y agregar histeresis antes de habilitar derivada.
- Estado posterior: follower activo, PWM/RPM=0 y fusion STOP conf=1.00 en ambas ruedas.
## 2026-08-21 - PI de velocidad V1 (prueba suspendida)

- Fusion ROS2: histeresis de 3 ventanas antes de cambiar OPTO/BLEND/HALL; prueba unitaria aprobada.
- Firmware: PI independiente por rueda aplicado como correccion sobre FF; Hall alimenta el lazo interno y odometria Hall/opto fusionada queda para el lazo exterior de posicion.
- Seguridad: PI apagado al arrancar; `k on`, `k off`, `k <Kp> <Ki>`; correccion limitada a +/-6 PWM; integral limitada a +/-30; D=0.
- Telemetria T agrega Ltrpm/Rtrpm, Lpi/Rpi y PI.
- A/B a 0.15 m/s (objetivo 10.6 RPM): PI off = L/R 31.2/31.2 RPM, PWM 15.2/15.2; Kp=0.15 = 25.5/26.2 RPM, PWM 12.9/12.8.
- Barrido Ki=0: Kp=0.25 -> 18.9/19.8 RPM, PWM 12.3/12.1; Kp=0.40 -> 20.0/20.9; Kp=0.60 -> 18.5/20.6. Se selecciona Kp=0.25.
- Candidata persistente: Kp=0.25, Ki=0, Kd=0; PI permanece desactivado hasta prueba con carga en suelo.
- Firmware final 62344 bytes, RAM 6760/8192 (82%, libres 1432), escrito y verificado por avrdude.
- Respaldo previo en Pi: `/home/josemsotov/robot_backups/pre_20260821_velocity_pi_v1.hex`.
- Scripts reproducibles: `run_velocity_pi_test.sh`, `run_velocity_pi_kp_sweep.sh`; logs en `.diagnostics/velocity_pi_*_20260821.log`.
- Estado final: follower activo, PWM/RPM=0, fusion STOP conf=1.00.

## 2026-08-21 - PI de velocidad V1 en suelo

- Robot probado en suelo con dos ruedas caster; sus tirones mecanicos se excluyen del criterio de ajuste.
- Stadia confirmo movimiento con PI apagado: en reversa PWM 12 no sostuvo RPM; ambas ruedas mostraron movimiento desde aproximadamente PWM 17. En avance el primer punto simultaneo capturado fue PWM 28-29 por falta de una rampa suficientemente fina.
- Rampa lenta de avance con PI apagado: PWM 10 produjo pulsos Hall esporadicos, sin regulacion continua.
- PI activado en runtime con k 0.25 0.0 y k on.
- Prueba PI en suelo: objetivo aproximado L=7.7/R=7.3 RPM; Hall alterno entre 0 y 11-13 RPM; correcciones tipicas Lpi/Rpi de 0 a aproximadamente -1.4 PWM; salida conmutando entre PWM 0/10/11.
- Diagnostico: el PI funciona, pero el estimador Hall actual usa ventanas de 100 ms y cuantiza demasiado a baja velocidad. No ajustar Kp/Ki sobre esta medicion.
- Proximo paso: estimador Hall hibrido (periodo entre pulsos a baja velocidad, conteo por ventana a velocidad media/alta), suavizado ligero y timeout explicito a cero; repetir la misma prueba A/B antes de ajustar Ki.
- Cierre de sesion: comando cero enviado, k off, Lpwm=0 Rpwm=0 Lrpm=0 Rrpm=0 y robot-follower.service activo.

## 2026-08-22 - Hall hibrido V2 y PI de baja velocidad V4

- Firmware instalado y verificado por `avrdude`: 63524 bytes flash; 6784/8192 bytes RAM (82%, 1408 libres).
- Estimador Hall hibrido: conteo por ventana con >=3 pulsos y periodo entre flancos a baja velocidad; suavizado y timeout adaptativo; flancos menores de 6000 us excluidos del estimador de velocidad.
- La temporizacion de velocidad Hall queda separada del intervalo usado por el filtro opto adaptativo, evitando picos falsos de 691-1120 RPM observados en V1.
- PWM subminimo: modulacion por densidad de pulsos con quantum determinista de 50 ms; el PI conserva demanda fraccional antes de convertirla a pulsos 0/10.
- Autoridad PI asimetrica: correccion positiva limitada a +6 PWM y negativa a -10 PWM. PI permanece apagado al arrancar y al finalizar pruebas.
- Barrido suspendido a 0.10 m/s, objetivo 7.1 RPM, Ki=0: Kp 0.25 = 14.82/15.45 RPM; Kp 0.50 = 12.12/13.04; Kp 0.75 = 11.73/12.35. Kp 1.0 y 1.5 no mejoraron porque las ruedas continuaron girando por inercia aun con duty cercano a cero.
- Candidato conservador para la siguiente prueba con carga: Kp=0.75, Ki=0. No dejarlo persistente ni activado hasta validar en suelo con rampa corta desde 0.06 m/s.
- Logs reproducibles: `.diagnostics/low_speed_kp_0.25.log`, `0.50`, `0.75`, `low_speed_v4_kp_0.75.log`, `low_speed_v4_highkp_1.00.log` y `1.50.log`.
- Estado final confirmado: `robot-follower.service` activo; `lin=0`, PWM L/R=0/0, RPM L/R=0/0.
- Proximo paso: colocar robot en suelo, despejar trayectoria y ejecutar escalon/rampa limitada a 0.06 m/s; comparar Kp 0.50 y 0.75 antes de introducir Ki.

## 2026-08-22 - Baseline V6 validado en suelo

- Se agrego boost de friccion estatica por flanco parada->movimiento: PWM 17 durante 500 ms; no se rearma durante la modulacion 0/10.
- Configuracion validada: comando 0.06 m/s, PI Kp=0.50 Ki=0, heading-hold temporal y 20 mensajes a 10 Hz.
- Prueba observada sin heading: 7.6 cm, giro a la izquierda; Hall L/R=4/6.
- Prueba observada con heading: 10.0 cm, trayectoria recta; Hall L/R=6/5, estimacion Hall=10.4 cm (error aproximado 4%).
- El heading-hold aplico correcciones suaves entre aproximadamente -0.006 y +0.013 rad/s; sin saturacion ni tirones observados.
- Los optos siguen sobrecontando a baja velocidad; para la siguiente prueba de posicion usar exclusivamente los conteos Hall crudos HL/HR.
- Estado final: motors PWM/RPM=0/0, fusion STOP, robot-follower.service activo; PI y heading desactivados por cleanup.
- Siguiente prueba: objetivo 20 cm = 10.61 pulsos Hall promedio; usar 11 pulsos como umbral y parada ROS inmediata, manteniendo PI Kp=0.50 y heading-hold.

## 2026-08-24 - Consola Fairway Trolley OS y nuevo repositorio base

- Interfaz redisenada en `simulation_ws/src/robot_operator_web/static/index.html`.
- Acceso: `http://192.168.40.74:8080/`; la portada muestra `FAIRWAY TROLLEY OS`.
- Areas separadas: Operacion, Pruebas y Entrenamiento; STOP siempre accesible.
- Datos de campo/hoyo persistidos localmente en el navegador; no hay aun backend multiusuario.
- Desplegada en las copias `src` e `install/share` de `robot_operator_web` en el Pi.
- Validacion: web activa, follower activo pero deshabilitado, salida automatica deshabilitada, modo STADIA, PWM/RPM 0/0, Kinect RGB/depth y LiDAR activos; GPS comunicando sin fix.
- Nuevo repositorio de continuidad: `https://github.com/josemsotov/Smart-trolley-AGO26-arduino-bridge-15.git`.
- Analisis funcional y hardware recomendado: `GOLF_OPERATOR_UI_ANALYSIS.md`.

## 2026-08-27 - PWM completo y rango Hall corregido

- Firmware operativo ampliado de `MAX_PWM_VALUE=40` al rango Timer5 completo `0..255`; control diferencial y comando diagnostico `q` tambien admiten hasta 255.
- Las rutinas de diagnostico del firmware principal dejaron de usar `analogWrite()` sobre 44/46 y usan `motor_pwm_write()`, que restaura los bits COM5A1/COM5C1 del Timer5.
- Firmware instalado y verificado por `avrdude`: 65470 bytes flash; RAM 6861/8192 bytes (83%, 1331 libres).
- Caracterizacion suspendida, tres repeticiones por PWM 10..90, guardada en `encoder_calibration_reports/controller_pwm_profile_20260827.{json,csv}`.
- En reposo durante 5 s: cero pulsos falsos Hall/opto. Entre PWM 20 y 80 ambos Hall mostraron velocidad practicamente simetrica.
- Se identifico que `HALL_SPEED_MIN_INTERVAL_US=6000` y `HALL_COUNT_MIN_INTERVAL_US=6000` rechazaban pulsos validos a PWM 90 (intervalo real aproximado 5850 us), dividiendo artificialmente el conteo Hall.
- Ambos umbrales Hall se redujeron a 2500 us, rango teorico aproximado de 533 RPM con 45 PPR. Validacion posterior:
  - PWM 60: L Hall/opto 109/126; R 109/110.
  - PWM 80: L 143/152; R 143/146.
  - PWM 90: L 159/170; R 158/160.
- Motores izquierdo y derecho respondieron nuevamente. Persisten 2..5 pulsos cruzados por ventana en la rueda detenida y exceso opto izquierdo aproximado de 6..15%; mantener fusion/fallback Hall.
- `PPR_OPTO_ENCODERS=45`, diametro de rueda 0.27 m y PWM completo 0..255 permanecen como configuracion activa.
- El test directo antiguo de PI por `pyserial` presenta `SerialTimeoutException` con el volumen actual de telemetria; no produjo movimiento. Ajuste PI siguiente debe ejecutarse mediante la ruta ROS normal o actualizar el protocolo de prueba.
- Estado al cierre: follower/web/Zenoh activos; motores PWM/RPM 0; robot suspendido.

## 2026-08-28 - Control virtual, Kinect y firmware FF120 V5

- La consola `FAIRWAY TROLLEY OS` incorpora en Pruebas una palanca virtual de movimiento y controles para tomar fotos y grabar video con Kinect.
- Acceso a la interfaz: `http://192.168.40.74:8080/`.
- La palanca publica a 20 Hz, emplea el perfil de ejes/deadzone/expo de Stadia y tiene prioridad temporal sobre Stadia mientras mantiene su deadman activo; Stadia recupera el control aproximadamente 0.35 s despues de cesar la entrada web.
- Se agrego el nodo piloto `swing_analyzer` y sus controles en el area Entrenamiento.
- Firmware FF120 V5: `FF_LEFT_GAIN`, `FF_RIGHT_GAIN`, `FF_LEFT_BWD_GAIN` y `FF_RIGHT_BWD_GAIN` configurados en 120. El limite electrico permanece en PWM 255.
- Con los limites web actuales, la palanca completa solicita aproximadamente PWM 48 en traslacion y PWM 34 en rotacion antes de correcciones PI.
- Se conserva el impulso de arranque PWM 25 durante 150 ms para vencer friccion estatica.
- Firmware compilado: 66006 bytes flash; RAM 6861/8192 bytes, 1331 libres.
- Firmware instalado y verificado en Arduino. Respaldo previo en Pi: `/home/josemsotov/robot_backups/pre_ff120_v5_20260828.hex`.
- Validacion posterior: `robot-follower.service` activo, puente Arduino recibiendo telemetria y motores detenidos con PWM/RPM 0/0.
- Siguiente accion: validar fisicamente recorridos cortos de avance, reversa y giro desde la palanca virtual, empezando con amplitud reducida.

## 2026-09-09 - Base de navegacion hibrida SLAM/GPS

- Agregados `hybrid_navigation.launch.py`, `slam_real.yaml` y `ekf_gps.yaml` al paquete `robot_follower`.
- Modos separados para evitar dos publicadores de `map -> odom`: `mapping` e `indoor` usan slam_toolbox; `outdoor` usa navsat_transform y EKF global.
- La salida autonoma/Nav2 queda deliberadamente deshabilitada hasta validar localizacion y la ruta de seguridad `/cmd_vel/navigation`.
- TF real completado con `base_link -> base_laser` en (-0.10, 0, 1.35 m) y `base_link -> gps_link` provisional en cero, pendiente medir la posicion de la antena.
- Archivos desplegados y paquete recompilado en el Pi. Stack reiniciado activo, LiDAR comunicado y motores PWM/RPM 0/0.
- Instalados en el Pi `ros-jazzy-slam-toolbox`, `ros-jazzy-navigation2`, `ros-jazzy-nav2-bringup` y `ros-jazzy-robot-localization`.
- Validacion interior aprobada: lifecycle manager configuro y activo `slam_toolbox`, que registro el LiDAR real sin publicar movimiento.
- Validacion exterior de arranque aprobada: `navsat_transform_node` y `ekf_global_filter` iniciaron sin fallo; falta validar posicion global con fix GPS estable al aire libre.
- Guia operativa y comandos: `simulation_ws/HYBRID_NAVIGATION.md`.

## 2026-09-10 - Respaldo SLAM, entrenamiento, Home Assistant y Stadia

- Mapa de dos habitaciones guardado como `two_rooms_20260909_2105` (PGM/YAML), 260x278 celdas a 5 cm; copia local en follower_sim/maps. Grafo SLAM NO guardado: conflicto de simbolo FastCDR en cliente SerializePoseGraph. No considerar localizacion exterior validada: solo se comprobo arranque de nodos, no precision GPS ni rumbo absoluto.
- Visor web SLAM con posicion TF y fallback a mapa guardado. Oculto en Entrenamiento; permanece en Operacion/Pruebas. API `/api/map`, vista compacta `/static/map.html`.
- Home Assistant `http://homeassistant.local:8123/smart-trolley/0` (192.168.40.198) usa estrategia iframe a la web del Pi. URL actualizada con version de cache. Respaldos HA en LocalAppData/SmartTrolley/ha-backups; token permanece fuera del repositorio.
- Stadia: curva lineal 1.6, aceleracion 0.20 m/s2 y 0.45 rad/s2; limites maximos 0.40 m/s y 0.70 rad/s. Paso por cero al invertir y STOP inmediato al soltar. Pruebas offline aprobadas, trayectoria fisica aun requiere ajuste.
- PI 0.25 sin integral y hc on se activaron temporalmente el 09-09. Usuario reporto vibracion; intento posterior de k off NO se ejecuto por bloqueo de cuota. Hubo reinicios posteriores: consultar Arduino antes de asumir estado PI/hc; no hay activacion persistente nueva.
- Coral recuperado tras reconexion USB: 18d1:9302, inferencias reales y coral_status=active. Fallo anterior de enumeracion USB, no del indicador web.
- Kinect: captura solicitada a 30 Hz, grabacion medida 25.81 fps (104 frames); ultima recepcion observada 28.7 fps. Vista previa sigue limitada a 4 Hz, analisis corporal a 10 Hz durante sesion/2 Hz inactivo.
- Entrenamiento: videos telefono hasta 300 MB, biblioteca, slow motion, paso aproximado por frames y marcas manuales exportables. Kinect clips hasta 30 s, AVI original, timestamps y MP4. Analisis telefono manual; no mide impacto, spin ni velocidad de bola/palo.
- Validacion: tres paquetes ROS compilados, upload sintetico 120 fps y rechazo de archivo invalido aprobados, clip Kinect real generado, motores 0/0 al cierre de despliegue. Documentacion detallada en TRAINING_VIDEO_20260910.md y MANUAL_DRIVE_TUNING_20260909.md.

## 2026-09-13 - TF-Luna commissioning firmware

- Soporte firmware local agregado para TF-Luna por I2C en `TF_Luna.h`, habilitado por comandos `tf status`, `tf on 1`, `tf off 1`, `tf on 2`, `tf off 2`.
- Direcciones previstas: canal 1 `0x10`, canal 2 `0x11`; ambos canales arrancan deshabilitados y no publican ni frenan el robot todavia.
- Firmware compilado: 68780 bytes flash; RAM 7125/8192 bytes, 1067 libres. SHA256 del HEX: `3fa43156fcc0d0c2456cde10084b70045d81070851e02c8961f07dde01ba902e`.
- Tests nativos del driver TF con Wire/Serial simulados pasaron: arranque deshabilitado, interlock de movimiento, firma, timeouts, rango, amplitud, error de dispositivo, stale y seleccion de canal 2.
- Firmware TF-Luna cargado y verificado por `avrdude`: 68780 bytes escritos y verificados. Respaldo previo de esta carga en Pi: `/home/josemsotov/robot_backups/pre_tfluna_20260913_5jjaKY/original.hex`; copia local `arduino_flash_backups/pre_tfluna_20260913_before_successful_upload.hex`; SHA256 `31170255871eeffa724f193b2e1cae259d177d026b25c27db85bff4444fc015b`. Respaldo previo adicional local `arduino_flash_backups/pre_tfluna_20260913_original.hex`; SHA256 `dfd72ef56f1fff65636438b1c88b4991ccf52e7ffef550453e931b8f2fa99fbd`.
- Usuario conecto solo el TF-Luna; IMU desconectado intencionalmente, por lo que `I ready=0` es esperado durante esta prueba.
- Verificacion fisica: Arduino Mega reaparecio como `/dev/ttyACM0`; comandos `tf` reconocidos. Canal1 `0x10` y canal2 `0x11` devuelven `err=2`, es decir NACK/timeout/lectura corta I2C, sin medicion valida.
- No se comandaron motores durante esta prueba. Siguiente paso: con power off, revisar VCC/GND, SDA/SCL a traves del level shifter, pin5 a GND, LV=3.3V, HV=lado Arduino, tierra comun y orientacion del conector; luego repetir `tf on 1`/`tf status` y despues reconectar/verificar MPU.
- Guia de cableado, comandos y protocolo: `TF_LUNA_INTEGRATION.md`.
