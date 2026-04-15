"""Launch file for Task 4 - Vision Line Follower with ROS2"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for vision line follower task."""
    
    # Vision Node
    vision_node = Node(
        package='task4_vision_line_follower',
        executable='vision_node',
        name='vision_line_follower_node',
        output='screen',
        parameters=[
            {'camera_topic': '/camera/image_raw'},
            {'base_speed': 50},
        ],
    )
    
    return LaunchDescription([
        vision_node,
    ])
