#!/usr/bin/env python3
"""Line sensor publisher node for Task 3 - Reads 5-channel line sensor array

This node reads the 5-channel digital line following sensor and publishes
the sensor data to the /line/sensors topic for other nodes to consume.
"""

import RPi.GPIO as GPIO
import time
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from robot_common.constants import LINE_SENSOR_PINS


class LineSensorPublisherNode(Node):
    """Node that reads line sensors and publishes data to ROS2 topic"""

    def __init__(self):
        """Initialize line sensor publisher node with real hardware"""
        super().__init__('line_sensor_publisher_node')

        # Initialize GPIO for line sensors
        try:
            self.line_pins = LINE_SENSOR_PINS
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            for pin in self.line_pins:
                GPIO.setup(pin, GPIO.IN)
            self.get_logger().info(f"✓ Line sensors initialized on pins {self.line_pins}")
        except Exception as e:
            self.get_logger().error(f"✗ Failed to initialize line sensors: {e}")
            raise

        # Create publisher for line sensor data
        self.publisher = self.create_publisher(
            String,
            '/line/sensors',
            10
        )

        # Declare parameters
        self.declare_parameter('publish_rate', 50)  # 50 Hz for responsive line following

        # Get parameters
        publish_rate = self.get_parameter('publish_rate').value
        publish_interval = 1.0 / publish_rate

        # Create timer for publishing
        self.create_timer(publish_interval, self.publish_callback)

        self.get_logger().info(f"Line sensor publisher initialized at {publish_rate} Hz")
        self.get_logger().info("Publishing line sensor data to /line/sensors topic")

    def publish_callback(self):
        """Timer callback to read and publish line sensor data"""
        try:
            # Read all 5 sensors (True = line detected, depends on sensor polarity)
            readings = [GPIO.input(pin) for pin in self.line_pins]

            # Build message
            msg = String()
            msg.data = json.dumps({
                'timestamp': time.time(),
                'sensors': readings,  # [left, left-center, center, right-center, right]
            })

            self.publisher.publish(msg)

            # Debug log
            sensor_str = ''.join(['█' if s else '░' for s in readings])
            self.get_logger().debug(f"Line: [{sensor_str}]")

        except Exception as e:
            self.get_logger().error(f"Failed to read line sensors: {e}")

    def destroy_node(self):
        """Clean up resources"""
        GPIO.cleanup()
        self.get_logger().info("Line sensor publisher cleanup complete.")
        super().destroy_node()


def main(args=None):
    """Main entry point - reads real line sensor hardware and publishes data"""
    rclpy.init(args=args)

    node = None
    try:
        node = LineSensorPublisherNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        if node:
            node.get_logger().info("\nShutting down line sensor publisher...")
    except Exception:
        pass
    finally:
        if node:
            node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
