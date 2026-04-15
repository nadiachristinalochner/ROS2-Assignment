#!/usr/bin/env python3
"""Motor control node for Task 2 — Use the IMU to drive the robot in a straight line.

This node subscribes to IMU data from /imu/data topic (published by imu_controller_node)
and applies PID control to maintain a straight heading by adjusting motor speeds.
"""

import sys
import time
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from robot_common import clamp
from robot_common.constants import KP, KI, KD


class IMUMotorControllerNode(Node):
    """Node that controls motors based on IMU feedback to drive in a straight line"""

    def __init__(self):
        """Initialize IMU motor controller node"""
        super().__init__('imu_motor_controller_node')

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
        self.get_logger().info("TASK 2: IMU-based straight line control")
        self.get_logger().info("=" * 60)

        # Subscribe to IMU data topic
        self.subscription = self.create_subscription(
            String,
            '/imu/data',
            self.imu_callback,
            10
        )

        # PID state
        self.heading_error = 0.0
        self.heading_integral = 0.0
        self.prev_yaw_rate = 0.0
        self.yaw_angle = 0.0

        # Timing
        self.imu_connected = False
        self.prev_imu_time = None
        self.start_time = None

        self.get_logger().info(f"Base speed: {self.base_speed}%")
        if self.duration:
            self.get_logger().info(f"Duration: {self.duration}s")
        else:
            self.get_logger().info("Duration: Infinite (press Ctrl+C to stop)")
        self.get_logger().info("Waiting for IMU data from /imu/data topic...")

    def calculate_motor_correction(self, yaw_rate):
        """Calculate motor speed correction based on yaw rate using PID control"""
        self.heading_error = yaw_rate
        self.heading_integral += self.heading_error
        self.heading_integral = clamp(self.heading_integral, -100, 100)

        derivative = yaw_rate - self.prev_yaw_rate
        self.prev_yaw_rate = yaw_rate

        correction = (KP * self.heading_error +
                     KI * self.heading_integral +
                     KD * derivative)

        motor_a_speed = clamp(self.base_speed + correction, -100, 100)
        motor_b_speed = clamp(self.base_speed - correction, -100, 100)

        return motor_a_speed, motor_b_speed

    def imu_callback(self, msg):
        """Callback for IMU data — applies PID correction to motors"""
        try:
            imu_dict = json.loads(msg.data)
            current_time = imu_dict['timestamp']

            if not self.imu_connected:
                self.imu_connected = True
                self.prev_imu_time = current_time
                self.start_time = time.time()
                self.get_logger().info("✓ Connected to IMU! Starting motor control...")
                return

            dt = current_time - self.prev_imu_time
            self.prev_imu_time = current_time

            if dt <= 0:
                return

            yaw_rate = imu_dict['gyro']['z']
            self.yaw_angle += yaw_rate * dt

            speed_a, speed_b = self.calculate_motor_correction(yaw_rate)
            self.motor_controller.set_motor_speeds(speed_a, speed_b)

            if self.duration is not None:
                elapsed = time.time() - self.start_time
                if elapsed >= self.duration:
                    self.get_logger().info(f"Duration {self.duration}s reached. Stopping motors...")
                    self.motor_controller.stop()
                    rclpy.shutdown()
                    return

            elapsed = time.time() - self.start_time
            self.get_logger().info(
                f"Heading: {self.yaw_angle:6.1f}° | Yaw: {yaw_rate:6.2f}°/s | "
                f"Motors: A={speed_a:3.0f}% B={speed_b:3.0f}% | Time: {elapsed:5.1f}s",
                throttle_duration_sec=0.5
            )

        except json.JSONDecodeError as e:
            self.get_logger().error(f"Failed to parse IMU message: {e}")
        except KeyError as e:
            self.get_logger().error(f"IMU message missing field: {e}")
        except Exception as e:
            self.get_logger().error(f"Error in IMU motor callback: {e}")
            import traceback
            traceback.print_exc()


def main(args=None):
    """Main entry point for Task 2 IMU motor control"""
    rclpy.init(args=args)

    node = None
    try:
        node = IMUMotorControllerNode()
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


