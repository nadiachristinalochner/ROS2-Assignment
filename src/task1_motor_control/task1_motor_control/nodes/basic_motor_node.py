#!/usr/bin/env python3
"""Basic Commander Node for Task 1 — publishes equal motor speeds to /motor/command.

This node does NOT directly control motors. It publishes speed commands
to the /motor/command topic, which the shared motor_controller_node consumes.

Publishes to: /motor/command  (JSON: {"left_speed": float, "right_speed": float})
"""

import time
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class BasicCommanderNode(Node):
    """Publishes constant equal-speed motor commands for Task 1"""

    def __init__(self):
        super().__init__('basic_commander_node')

        # Declare parameters
        self.declare_parameter('base_speed', 80)
        self.declare_parameter('duration', -1.0)  # -1 means infinite

        # Get parameters
        self.base_speed = self.get_parameter('base_speed').value
        duration = self.get_parameter('duration').value
        self.duration = None if duration < 0 else duration

        # Publisher to /motor/command (consumed by motor_controller_node)
        self.cmd_publisher = self.create_publisher(String, '/motor/command', 10)

        self.get_logger().info("=" * 60)
        self.get_logger().info("TASK 1: Basic Motor Control")
        self.get_logger().info("Publishing equal speeds to /motor/command")
        self.get_logger().info("=" * 60)
        self.get_logger().info(f"Base speed: {self.base_speed}%")
        if self.duration:
            self.get_logger().info(f"Duration: {self.duration}s")
        else:
            self.get_logger().info("Duration: Infinite (Ctrl+C to stop)")

        self.start_time = time.time()

        # Publish motor commands at 10 Hz
        self.create_timer(0.1, self.publish_command)

    def publish_command(self):
        """Publish equal motor speed command"""
        elapsed = time.time() - self.start_time

        # Check if duration has elapsed
        if self.duration is not None and elapsed >= self.duration:
            # Send stop command then shutdown
            stop_msg = String()
            stop_msg.data = json.dumps({'left_speed': 0.0, 'right_speed': 0.0})
            self.cmd_publisher.publish(stop_msg)
            self.get_logger().info(f"Duration {self.duration}s reached. Stopping.")
            rclpy.shutdown()
            return

        # Publish equal speed command
        msg = String()
        msg.data = json.dumps({
            'left_speed': float(self.base_speed),
            'right_speed': float(self.base_speed),
        })
        self.cmd_publisher.publish(msg)

        self.get_logger().info(
            f"CMD: L={self.base_speed}% R={self.base_speed}% | Time: {elapsed:.1f}s",
            throttle_duration_sec=2.0
        )


def main(args=None):
    """Main entry point for Task 1 basic commander"""
    rclpy.init(args=args)

    node = None
    try:
        node = BasicCommanderNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        if node:
            node.get_logger().info("\nStopping...")
            # Send stop command before exiting
            try:
                stop_msg = String()
                stop_msg.data = json.dumps({'left_speed': 0.0, 'right_speed': 0.0})
                node.cmd_publisher.publish(stop_msg)
            except Exception:
                pass
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
