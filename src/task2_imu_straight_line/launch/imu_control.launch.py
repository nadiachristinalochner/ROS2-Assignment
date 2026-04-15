"""Launch file for Task 2 - IMU Straight Line Control with Topic-based Communication"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import FindExecutable
from launch.actions import ExecuteProcess


def generate_launch_description():
    """Generate launch description for IMU straight line task."""
    
    # IMU Publisher Node
    imu_node = Node(
        package='task2_imu_straight_line',
        executable='imu_controller_node',
        name='imu_publisher_node',
        output='screen',
        parameters=[
            {'calibration_count': 100},
            {'publish_rate': 20},
        ],
    )
    
    # Motor Controller Node
    motor_node = Node(
        package='task1_motor_control',
        executable='motor_node',
        name='motor_controller_node',
        output='screen',
        parameters=[
            {'base_speed': 50},
        ],
    )
    
    return LaunchDescription([
        imu_node,
        motor_node,
    ])

