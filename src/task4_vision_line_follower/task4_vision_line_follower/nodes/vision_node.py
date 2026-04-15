#!/usr/bin/env python3
"""Vision node for Task 4 - Camera-Based Line Following with ROS2

This node captures frames from the Pi Camera and uses OpenCV to detect
and follow a line using computer vision. Publishes and subscribes to ROS2 topics.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class VisionLineFollowerNode(Node):
    """Node for vision-based line following"""
    
    def __init__(self):
        """Initialize vision node"""
        super().__init__('vision_line_follower_node')
        
        # Declare parameters
        self.declare_parameter('camera_topic', '/camera/image_raw')
        self.declare_parameter('base_speed', 50)
        
        # Get parameters
        camera_topic = self.get_parameter('camera_topic').value
        self.base_speed = self.get_parameter('base_speed').value
        
        # Initialize CV bridge
        self.bridge = CvBridge()
        
        # Create subscription to camera images
        self.image_subscription = self.create_subscription(
            Image,
            camera_topic,
            self.image_callback,
            10
        )
        
        self.get_logger().info(f"Vision line follower node initialized")
        self.get_logger().info(f"Subscribing to {camera_topic}")
    
    def image_callback(self, msg):
        """Callback for image subscription
        
        Args:
            msg: ROS2 Image message
        """
        try:
            # Convert ROS image to OpenCV image
            # cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # TODO: Implement line detection logic
            # TODO: Calculate motor speeds based on line position
            # TODO: Publish motor commands
            
            self.get_logger().debug(f"Received image: {msg.width}x{msg.height}")
        
        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")
    
    def destroy_node(self):
        """Clean up resources"""
        self.get_logger().info("Vision line follower node cleanup complete.")
        super().destroy_node()


def main(args=None):
    """Main entry point"""
    rclpy.init(args=args)
    
    node = VisionLineFollowerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down vision node...")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

