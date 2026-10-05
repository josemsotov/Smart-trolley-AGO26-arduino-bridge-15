# Identificacion de dos LiDAR — 2026-09-16

> Estado supersedido el 2026-10-05: el LiDAR inferior fue desconectado y su
> puerto físico se reasignó a la cámara ELP global-shutter. El launch activo lo
> deja deshabilitado por defecto y la interfaz lo identifica como desactivado.
> El contenido siguiente conserva la evidencia histórica de la integración dual.

Estado actual: ambos LiDAR transmiten a 10 Hz y aparecen en la interfaz web.
No esta validado el inferior para navegacion/evasion.

## Recuperacion y web

Usuario confirma reconexion del sensor y solicita incorporarlo a la interfaz.
Tras reiniciar el stack: auditoria simultanea aprobada, superior 117 mensajes
a 9.92 Hz, inferior 116 a 10.00 Hz. TF inferior confirmado: (-0.10, 0, 0.15),
cuaternion (1, 0, 0, ~0). x/y siguen provisionales.

Interfaz `http://192.168.40.74:8080/`: panel inferior en Operacion con vista
polar, estado, Hz, puntos, minimo frontal +/-60 grados y minimo 360 grados;
estado adicional en servicios de Operacion y Pruebas. Backend publica
`scan_lower` y `ages.scan_lower` por los canales existentes de estado.
Vista inferior corrige roll pi, ambos dibujos usan izquierda a la izquierda.
Sector frontal normalizado para incluir ambos lados de cero (0/2pi).
Lecturas de mas de 1 segundo se ocultan del dibujo inferior y sus metricas.

Verificado HTTP 200 para recurso JS y portada con canvas; API real:
ambos 10 Hz, edades superior 0.010 s/inferior 0.091 s, inferior 301 puntos
validos y minimo frontal 0.025 m. Ese retorno cercano requiere inspeccionar
montaje/obstaculos antes de incorporarlo a frenado. No se comandaron motores.
Prueba `test_dual_lidar_web.py` aprobada (inversion, independencia, wraparound,
rangos invalidos), sintaxis Python/JavaScript aprobada. No hubo verificacion
visual con navegador automatizado. JS instalado en src y install/share.
Respaldos Pi: `robot_backups/web_server.pre_dual_lidar_20260916.py` y
`robot_backups/index.pre_dual_lidar_20260916.html`.

## Montaje e intento de activacion, 20:33 BST

- Usuario confirma segundo LD19, invertido, flecha hacia adelante, altura 15 cm.
- Driver inferior habilitado por defecto, `/scan_lower`, `base_laser_lower`.
- TF: roll pi, pitch/yaw cero. Inversion aplicada solo en TF; se conserva
  `laser_scan_dir=true` para no corregir dos veces.
- z=0.15 interpretado como plano de escaneo sobre suelo; base_link usa z=0.
- x=-0.10, y=0 PROVISIONALES: alineado debajo del superior hasta medir montaje.
- Respaldo Pi: `robot_backups/follower.launch.pre_lower_enable_20260916.py`.
- Sintaxis validada y stack reiniciado. Auditoria pasiva de 12 s: superior
  120 mensajes, 10.00 Hz, 455 puntos/439 validos, TF superior correcto.
- Inferior: cero mensajes; driver abre puerto 1.4 pero termina con
  `ldlidar communication is abnormal` tras 3 s.
- Puerto inferior libre confirmado con fuser. Prueba serie exclusiva a 230400:
  CERO bytes en 5 s. Revisar alimentacion, giro, conector y enlace TX del sensor
  al adaptador antes de repetir. La causa fisica aun no esta determinada.
- Scripts: `audit_dual_lidar.py`, `run_dual_lidar_audit.sh`,
  `probe_lower_lidar_serial.py` (este ultimo solo con driver inferior detenido).
- No se fusionaron escaneos ni se modifico SLAM/evasion. Falta recepcion inferior,
  medir x/y y validar frente/izquierda/derecha con objetos conocidos.
- El proceso inferior termina ante timeout: tras corregir hardware reiniciar
  robot-follower.service de usuario para repetir. No se comandaron motores.

## Actualizacion 20:12–20:15 BST

Ambos adaptadores conectados: original en puerto `1.3` (`ttyUSB0`) y segundo
en `1.4` (`ttyUSB2`). Ambos repiten VID:PID y serie `0001`; el enlace by-id
apuntaba al segundo. Se corrige `follower.launch.py` para usar by-path del
original, con argumento `lidar_upper_port` configurable.

Se agrega driver inferior condicionado por `enable_lidar_lower` (false por
defecto), puerto 1.4, topico `/scan_lower`, frame `base_laser_lower`, producto
y baud configurables. LD19/230400 son valores candidatos, pendientes de
confirmacion del usuario. No se publica TF inferior sin medidas de montaje.

Archivo desplegado en Pi, sintaxis Python validada y servicio de usuario
reiniciado activo. Respaldo previo:
`/home/josemsotov/robot_backups/follower.launch.pre_dual_lidar_20260916.py`.
Arduino ausente por USB y Kinect sin frames; no se enviaron comandos motores.
Activacion del inferior, comprobacion simultanea de scans e integracion en
evasion siguen pendientes del modelo y geometria.

## Original / superior

Usuario confirma que solo el original esta conectado. Consulta SSH al Pi
192.168.40.74 a las 20:10–20:11 BST:

- Adaptador: Silicon Labs CP2102, VID:PID `10c4:ea60`.
- Numero de serie USB: `0001`.
- Dispositivo actual: `/dev/ttyUSB2` (enumeracion temporal, no usar como identidad).
- `ID_PATH`: `platform-xhci-hcd.1-usb-0:1.3:1.0`.
- Ruta persistente por puerto:
  `/dev/serial/by-path/platform-xhci-hcd.1-usb-0:1.3:1.0-port0`.
- Puerto fisico kernel: `4-1.3`.
- Configuracion existente: LD19, 230400 baud, `/scan`, `base_laser`.

La identificacion USB corresponde al adaptador, no confirma el modelo optico
ni la recepcion de medidas.

## Segundo / inferior pendiente

Antes de conectar solo el original se observo un CP2102 con serie `0001`
en `platform-xhci-hcd.1-usb-0:1.4:1.0`, entonces `/dev/ttyUSB0`.
Confirmar conectando el nuevo: no asignar aun esa identidad al sensor inferior.

Si ambos adaptadores repiten `0001`, el enlace `by-id` no distingue sensores.
Usar rutas `by-path` o alias udev basados en puerto fisico y etiquetar cables
y puertos. Esta asignacion exige conservar los puertos USB.

Pendiente: identificar el segundo, confirmar modelo, medir posicion y
orientacion inferior, configurar `/scan_lower` y `base_laser_lower`, validar
ambas lecturas simultaneas antes de incorporar datos a evasion de obstaculos.

Los servicios ROS/web/Zenoh son servicios de usuario (`systemctl --user`);
estan activos. No se han comandado motores ni reiniciado servicios en esta
identificacion.
