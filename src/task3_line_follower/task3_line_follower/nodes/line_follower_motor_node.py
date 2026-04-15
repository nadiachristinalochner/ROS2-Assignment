#!/usr/bin/env python3
"""Line follower motor controller node for Task 3

This node subscribes to line sensor data from /line/sensors topic
and applies PID control to follow the line by adjusting motor speeds.
"""

import sys
import time
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from robot_common import clamp, line_sensor_position
from robot_common.constants import LINE_KP, LINE_KI, LINE_KD


class LineFollowerMotorNode(Node):
    """Node that controls motors based on line sensor data from ROS2 topic"""

    def __init__(self):
        """Initialize line follower motor controller node"""
        super().__init__('line_follower_motor_node')

        # Initialize real motor controller
        try:
            from robot_hardware_interface import MotorController
            self.motor_controller = MotorController()
            self.get_logger().info("✓ Motor controller initialized")
        except Exception as e:
            self.get_logger().error(f"✗ Failed to initialize motor controller: {e}")
            raise

        # Declare parameters
        self.declare_parameter('base_speed', 50)
        self.declare_parameter('duration', -1.0)  # -1 means infinite

        # Get parameters
        self.base_speed = self.get_parameter('base_speed').value
        duration = self.get_parameter('duration').value
        self.duration = None if duration < 0 else duration

        self.get_logger().info("=" * 60)
        self.get_logger().info("MODE: Line following control")
        self.get_logger().info("=" * 60)

        # Subscribe to line sensor data topic
        self.subscription = self.create_subscription(
            String,
            '/line/sensors',
            self.line_callback,
            10
        )

        # PID state
        self.prev_error = 0.0
        self.integral = 0.0

        # Tracking
        self.connected = False
        self.start_time = None
        self.no_line_count = 0
        self.last_known_direction = 0.0  # Remember last direction for recovery

        self.get_logger().info(f"Base speed: {self.base_speed}%")
        self.get_logger().info(f"PID: KP={LINE_KP}, KI={LINE_KI}, KD={LINE_KD}")
        if self.duration:
            self.get_logger().info(f"Duration: {self.duration}s")
        else:
            self.get_logger().info("Duration: Infinite (press Ctrl+C to stop)")
        self.get_logger().info("Waiting for line sensor data from /line/sensors topic...")

    def line_callback(self, msg):
        """Callback for line sensor data subscription"""
        try:
            # Parse JSON message
            data = json.loads(msg.data)
            sensors = data['sensors']

            # First message - mark connected
            if not self.connected:
                self.connected = True
                self.start_time = time.time()
                self.get_logger().info("✓ Connected to line sensors! Starting line following...")

            # Calculate position error using weighted average
            # Returns -2 (far left) to +2 (far right), 0 = centered
            position_error = line_sensor_position(sensors)
            line_detected = any(sensors)

            if not line_detected:
                # No line detected - keep moving forward and turn toward last known direction
                self.no_line_count += 1
                if self.no_line_count > 150:  # ~3 seconds at 50Hz
                    # Lost line for too long - stop
                    self.motor_controller.stop()
                    self.get_logger().warn(
                        "⚠ Line lost! Stopping motors. Reposition robot on line.",
                        throttle_duration_sec=2.0
                    )
                    return
                else:
                    # Recovery: drive forward while turning hard toward last known direction
                    turn_dir = 1.0 if self.last_known_direction >= 0 else -1.0
                    # Inner wheel slow, outer wheel at base_speed = arc turn (keeps moving)
                    inner = max(self.base_speed * 0.15, 10)
                    outer = self.base_speed
                    if turn_dir > 0:
                        self.motor_controller.set_motor_speeds(inner, outer)
                    else:
                        self.motor_controller.set_motor_speeds(outer, inner)
                    self.get_logger().info(
                        f"Searching {'right' if turn_dir > 0 else 'left'}...",
                        throttle_duration_sec=0.5
                    )
                    return
            else:
                self.no_line_count = 0
                if position_error != 0:
                    self.last_known_direction = position_error

            # Dynamic speed: gentle slowdown on curves, keep at least 75% of base speed
            error_magnitude = abs(position_error)
            speed_factor = max(0.75, 1.0 - 0.125 * error_magnitude)
            dynamic_speed = self.base_speed * speed_factor

            # PID control with non-linear boost for large errors
            self.integral += position_error
            self.integral = clamp(self.integral, -50, 50)  # Anti-windup

            derivative = position_error - self.prev_error
            self.prev_error = position_error

            # Boost correction at edges (squared term adds urgency)
            correction = (LINE_KP * position_error +
                         LINE_KI * self.integral +
                         LINE_KD * derivative +
                         3.0 * position_error * error_magnitude)  # Non-linear boost

            # Apply correction to motor speeds
            # Positive error = line is to the right = turn right = slow right motor (A)
            motor_a_speed = clamp(dynamic_speed - correction, -100, 100)
            motor_b_speed = clamp(dynamic_speed + correction, -100, 100)

            # Set motor speeds
            self.motor_controller.set_motor_speeds(motor_a_speed, motor_b_speed)

            # Check duration
            if self.duration is not None:
                elapsed = time.time() - self.start_time
                if elapsed >= self.duration:
                    self.get_logger().info(f"Duration {self.duration}s reached. Stopping.")
                    self.motor_controller.stop()
                    rclpy.shutdown()
                    return

            # Log status
            elapsed = time.time() - self.start_time
            sensor_str = ''.join(['█' if s else '░' for s in sensors])
            self.get_logger().info(
                f"Line: [{sensor_str}] | Pos: {position_error:+5.2f} | "
                f"Motors: A={motor_a_speed:3.0f}% B={motor_b_speed:3.0f}% | "
                f"Time: {elapsed:5.1f}s",
                throttle_duration_sec=0.5
            )

        except json.JSONDecodeError as e:
            self.get_logger().error(f"Failed to parse line sensor message: {e}")
        except KeyError as e:
            self.get_logger().error(f"Line sensor message missing field: {e}")
        except Exception as e:
            self.get_logger().error(f"Error in line follower callback: {e}")
            import traceback
            traceback.print_exc()


def main(args=None):
    """Main entry point"""
    rclpy.init(args=args)

    node = None
    try:
        node = LineFollowerMotorNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        if node:
            node.get_logger().info("\nInterrupted. Stopping motors...")
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
