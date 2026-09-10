import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def _is_mode(name):
    return IfCondition(PythonExpression(["'", LaunchConfiguration('mode'), "' == '", name, "'"]))


def generate_launch_description():
    pkg = get_package_share_directory('robot_follower')
    slam_params = LaunchConfiguration('slam_params_file')
    gps_params = LaunchConfiguration('gps_params_file')
    map_file = LaunchConfiguration('map_file')
    use_nav2 = LaunchConfiguration('use_nav2')

    actions = [
        DeclareLaunchArgument(
            'mode', default_value='mapping',
            description='mapping, indoor or outdoor'),
        DeclareLaunchArgument(
            'slam_params_file',
            default_value=os.path.join(pkg, 'config', 'slam_real.yaml')),
        DeclareLaunchArgument(
            'gps_params_file',
            default_value=os.path.join(pkg, 'config', 'ekf_gps.yaml')),
        DeclareLaunchArgument(
            'map_file', default_value='',
            description='Serialized slam_toolbox pose-graph for indoor mode'),
        DeclareLaunchArgument(
            'use_nav2', default_value='false',
            description='Safety gate. Start Nav2 separately only after localization validation.'),

        Node(
            package='slam_toolbox', executable='async_slam_toolbox_node',
            name='slam_toolbox', output='screen',
            parameters=[slam_params, {'mode': 'mapping'}],
            condition=_is_mode('mapping')),
        Node(
            package='slam_toolbox', executable='localization_slam_toolbox_node',
            name='slam_toolbox', output='screen',
            parameters=[slam_params, {'mode': 'localization',
                                      'map_file_name': map_file}],
            condition=_is_mode('indoor')),
        Node(
            package='nav2_lifecycle_manager', executable='lifecycle_manager',
            name='lifecycle_manager_slam', output='screen',
            parameters=[{'autostart': True,
                         'bond_timeout': 0.0,
                         'node_names': ['slam_toolbox']}],
            condition=IfCondition(PythonExpression([
                "'", LaunchConfiguration('mode'), "' in ['mapping', 'indoor']"
            ]))),

        Node(
            package='robot_localization', executable='navsat_transform_node',
            name='navsat_transform', output='screen',
            parameters=[gps_params],
            remappings=[('imu/data', '/imu/data_raw'),
                        ('gps/fix', '/fix'),
                        ('odometry/filtered', '/odometry/filtered'),
                        ('odometry/gps', '/odometry/gps')],
            condition=_is_mode('outdoor')),
        Node(
            package='robot_localization', executable='ekf_node',
            name='ekf_global_filter', output='screen',
            parameters=[gps_params],
            remappings=[('odometry/filtered', '/odometry/global')],
            condition=_is_mode('outdoor')),

        # This node deliberately does not command motors. The argument is
        # retained as an explicit safety gate for the later Nav2 bringup.
        Node(
            package='robot_follower', executable='field_supervisor',
            name='navigation_safety_observer', output='screen',
            condition=IfCondition(use_nav2)),
    ]
    return LaunchDescription(actions)
