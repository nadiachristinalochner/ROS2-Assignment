"""Launch file for Task 3 - Line Follower with ROS2

Launches two nodes:
1. Line Sensor Publisher - reads sensors, publishes to /line/sensors
2. Line Follower Motor Controller - subscribes to /line/sensors, controls motors
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for line follower task."""

    # Line Sensor Publisher Node
    line_sensor_publisher = Node(
        package='task3_line_follower',
        executable='line_sensor_publisher_node',
        name='line_sensor_publisher_node',
        output='screen',
        parameters=[
            {'publish_rate': 50},
        ],
    )

    # Line Follower Motor Controller Node
    line_follower_motor = Node(
        package='task3_line_follower',
        executable='line_follower_motor_node',
        name='line_follower_motor_node',
        output='screen',
        parameters=[
            {'base_speed': 50},
            {'duration': -1.0},
        ],
    )

    return LaunchDescription([
        line_sensor_publisher,
        line_follower_motor,
    ])
