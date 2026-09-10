# Navegacion hibrida del Smart Trolley

La implementacion separa la localizacion de la autorizacion de movimiento. Al
instalarla, ningun modo de navegacion publica comandos a los motores.

## Sensores y modos

- `mapping`: LiDAR LD19 + odometria fusionada + IMU local. Genera `map -> odom`
  con `slam_toolbox` mientras el operador conduce con Stadia o la interfaz web.
- `indoor`: carga un pose-graph de `slam_toolbox` y localiza el trolley dentro
  de un mapa previamente levantado.
- `outdoor`: combina `/fix`, `/imu/data_raw` y `/odometry/filtered` mediante
  `navsat_transform_node` y un EKF global. Publica `/odometry/global` y
  `map -> odom`.

No ejecutar SLAM interior y EKF GPS exterior simultaneamente: ambos son dueños
de la transformacion `map -> odom`.

## Paquetes requeridos en el Pi

```bash
sudo apt update
sudo apt install ros-jazzy-slam-toolbox ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup ros-jazzy-robot-localization
```

## Inicio seguro

Con el stack normal activo y el control autonomo deshabilitado:

```bash
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash
ros2 launch robot_follower hybrid_navigation.launch.py mode:=mapping
```

Conduzca manualmente cerrando circuitos y regresando al punto inicial. Para
guardar el pose-graph y el mapa:

```bash
mkdir -p ~/robot_ws/maps
ros2 service call /slam_toolbox/serialize_map \
  slam_toolbox/srv/SerializePoseGraph "{filename: '$HOME/robot_ws/maps/course'}"
ros2 run nav2_map_server map_saver_cli -f ~/robot_ws/maps/course
```

Localizacion interior posterior:

```bash
ros2 launch robot_follower hybrid_navigation.launch.py \
  mode:=indoor map_file:=$HOME/robot_ws/maps/course
```

Localizacion exterior:

```bash
ros2 launch robot_follower hybrid_navigation.launch.py mode:=outdoor
```

Antes de aceptar la salida exterior deben observarse al menos seis satelites,
HDOP <= 2.5 y un fix estable durante 10 s. El NEO-6M no ofrece precision
centimetrica: es apropiado para referencia global y geocercas amplias, mientras
el LiDAR mantiene evitacion local. Para seguir carriles o bordes estrechos se
recomienda GNSS RTK.

## Validaciones antes de habilitar Nav2

1. Confirmar una sola cadena TF: `map -> odom -> base_link -> base_laser`.
2. Verificar que el mapa no se deforme en avance, reversa y giro lento.
3. Medir deriva al regresar al punto inicial y repetir en tres recorridos.
4. Confirmar que retirar GPS no genera saltos ni comandos de movimiento.
5. Ajustar la posicion fisica `base_link -> gps_link`; actualmente queda en
   cero hasta medir el desplazamiento real de la antena.
6. Integrar Nav2 a `/cmd_vel/navigation` dentro del mux y validar takeover,
   deadman, STOP y limite de velocidad en banco antes de cualquier prueba en
   suelo.
