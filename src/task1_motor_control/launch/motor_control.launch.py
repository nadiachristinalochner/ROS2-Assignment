"""Launch file for Task 1 - Motor Control with IMU Feedback using Topics"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for motor control with IMU feedback."""
    
    # IMU Publisher Node (Task 2)
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
    
    # Motor Controller Node (Task 1)
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

