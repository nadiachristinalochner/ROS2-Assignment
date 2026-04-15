#!/usr/bin/env python3
"""Shared Motor Controller Node — actuates motors based on /motor/command topic.

Used by BOTH Task 1 and Task 2. Different upstream publisher nodes send commands:
  - Task 1: basic_commander_node sends equal speeds
  - Task 2: imu_controller_node sends PID-corrected speeds

Subscribes to: /motor/command  (JSON: {"left_speed": float, "right_speed": float})
Publishes to:  /motor/status   (JSON: current speeds + command count)

Includes a safety timeout — stops motors if no command is received within the timeout.
"""

import time
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MotorControllerNode(Node):
    """Receives motor commands from /motor/command and actuates the hardware"""

    def __init__(self):
        super().__init__('motor_controller_node')

        # Initialize motor hardware
        try:
            from robot_hardware_interface import MotorController
            self.motor_controller = MotorController()
            self.get_logger().info("✓ Motor controller hardware initialized")
        except Exception as e:
            self.get_logger().error(f"✗ Failed to initialize motor controller: {e}")
            raise

        # Subscribe to motor commands
        self.cmd_subscription = self.create_subscription(
            String,
            '/motor/command',
            self.command_callback,
            10
        )

        # Publisher for motor status (monitoring via rqt_graph / ros2 topic echo)
        self.status_publisher = self.create_publisher(
            String,
            '/motor/status',
            10
        )

        # State
        self.current_left = 0.0
        self.current_right = 0.0
        self.last_cmd_time = None
        self.cmd_count = 0

        # Safety timeout: stop motors if no command received within this period
        self.declare_parameter('safety_timeout', 1.0)
        self.safety_timeout = self.get_parameter('safety_timeout').value
        self.create_timer(0.2, self.safety_check)  # Check 5 times per second

        # Status publishing at 2 Hz
        self.create_timer(0.5, self.publish_status)

        self.get_logger().info("=" * 60)
        self.get_logger().info("MOTOR CONTROLLER NODE (shared)")
        self.get_logger().info("Listening on /motor/command")
        self.get_logger().info("Publishing to /motor/status")
        self.get_logger().info(f"Safety timeout: {self.safety_timeout}s")
        self.get_logger().info("=" * 60)

    def command_callback(self, msg):
        """Receive and execute a motor command"""
        try:
            cmd = json.loads(msg.data)
            left_speed = float(cmd['left_speed'])
            right_speed = float(cmd['right_speed'])

            self.motor_controller.set_motor_speeds(left_speed, right_speed)
            self.current_left = left_speed
            self.current_right = right_speed
            self.last_cmd_time = time.time()
            self.cmd_count += 1

        except (json.JSONDecodeError, KeyError) as e:
            self.get_logger().error(f"Bad motor command: {e}")
        except Exception as e:
            self.get_logger().error(f"Motor command error: {e}")

    def safety_check(self):
        """Stop motors if no command received within timeout"""
        if self.last_cmd_time is None:
            return  # Haven't received any commands yet

        elapsed = time.time() - self.last_cmd_time
        if elapsed > self.safety_timeout:
            if self.current_left != 0.0 or self.current_right != 0.0:
                self.get_logger().warn(
                    f"No motor command for {elapsed:.1f}s — stopping motors (safety)")
                self.motor_controller.stop()
                self.current_left = 0.0
                self.current_right = 0.0

    def publish_status(self):
        """Publish current motor status for monitoring"""
        msg = String()
        msg.data = json.dumps({
            'timestamp': time.time(),
            'left_speed': self.current_left,
            'right_speed': self.current_right,
            'commands_received': self.cmd_count,
        })
        self.status_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = None
    try:
        node = MotorControllerNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        if node:
            node.get_logger().info("\nStopping motors...")
    except Exception:
        pass
    finally:
        if node:
            if node.motor_controller:
                node.motor_controller.stop()
                node.motor_controller.cleanup()
            node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
