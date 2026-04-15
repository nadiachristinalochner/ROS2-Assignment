#!/usr/bin/env python3
"""IMU Controller Node for Task 2 — reads IMU, applies PID, publishes motor commands.

This node:
1. Reads IMU hardware and publishes raw data to /imu/data (for monitoring)
2. Applies PID control based on gyroscope yaw rate to maintain a straight heading
3. Publishes corrected motor speeds to /motor/command (consumed by motor_controller_node)

Publishes to: /imu/data       (JSON: raw accelerometer + gyroscope data)
              /motor/command   (JSON: {"left_speed": float, "right_speed": float})
"""

import time
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from robot_hardware_interface import IMUSensor
from robot_common import clamp
from robot_common.constants import KP, KI, KD


class IMUControllerNode(Node):
    """Reads IMU, applies PID, publishes corrected motor commands"""

    def __init__(self):
        super().__init__('imu_controller_node')

        # Initialize IMU hardware
        try:
            self.imu = IMUSensor()
            self.get_logger().info("✓ IMU initialized successfully")
        except Exception as e:
            self.get_logger().error(f"✗ Failed to initialize IMU: {e}")
            raise

        # Publishers
        self.imu_publisher = self.create_publisher(String, '/imu/data', 10)
        self.cmd_publisher = self.create_publisher(String, '/motor/command', 10)

        # Parameters
        self.declare_parameter('calibration_count', 100)
        self.declare_parameter('publish_rate', 20)
        self.declare_parameter('base_speed', 50)
        self.declare_parameter('duration', -1.0)  # -1 means infinite

        calibration_count = self.get_parameter('calibration_count').value
        publish_rate = self.get_parameter('publish_rate').value
        self.base_speed = self.get_parameter('base_speed').value
        duration = self.get_parameter('duration').value
        self.duration = None if duration < 0 else duration

        # Gyro calibration
        self.gyro_offset = [0.0, 0.0, 0.0]
        self.is_calibrated = False
        self.calibration_samples = 0
        self.calibration_count = calibration_count
        self.calibration_sum = [0.0, 0.0, 0.0]

        # PID state
        self.heading_error = 0.0
        self.heading_integral = 0.0
        self.prev_yaw_rate = 0.0
        self.yaw_angle = 0.0

        # Timing
        self.publish_interval = 1.0 / publish_rate
        self.prev_time = None
        self.start_time = None

        # Timer for reading IMU + publishing at desired rate
        self.create_timer(self.publish_interval, self.control_callback)

        self.get_logger().info("=" * 60)
        self.get_logger().info("TASK 2: IMU Straight Line Controller")
        self.get_logger().info("Publishing IMU data to /imu/data")
        self.get_logger().info("Publishing motor commands to /motor/command")
        self.get_logger().info("=" * 60)
        self.get_logger().info(f"Base speed: {self.base_speed}%")
        if self.duration:
            self.get_logger().info(f"Duration: {self.duration}s")
        else:
            self.get_logger().info("Duration: Infinite (Ctrl+C to stop)")
        self.get_logger().info(f"PID gains: KP={KP}, KI={KI}, KD={KD}")

    def calibrate_gyro(self):
        """Calibrate gyroscope by sampling and averaging"""
        try:
            gyro = self.imu.read_gyroscope()
            for i in range(3):
                self.calibration_sum[i] += gyro[i]
            self.calibration_samples += 1

            progress = (self.calibration_samples / self.calibration_count) * 100
            self.get_logger().info(f"Calibrating: {progress:.0f}%", throttle_duration_sec=1.0)

            if self.calibration_samples >= self.calibration_count:
                for i in range(3):
                    self.gyro_offset[i] = self.calibration_sum[i] / self.calibration_count
                self.is_calibrated = True
                self.start_time = time.time()
                self.get_logger().info("✓ Calibration complete!")
                self.get_logger().info(
                    f"Gyro offsets: X={self.gyro_offset[0]:.4f}, "
                    f"Y={self.gyro_offset[1]:.4f}, Z={self.gyro_offset[2]:.4f} deg/s")
                self.get_logger().info("Starting PID motor control...")
        except Exception as e:
            self.get_logger().error(f"Calibration error: {e}")

    def calculate_motor_correction(self, yaw_rate):
        """PID control to maintain straight heading"""
        self.heading_error = yaw_rate
        self.heading_integral += self.heading_error
        self.heading_integral = clamp(self.heading_integral, -100, 100)

        derivative = yaw_rate - self.prev_yaw_rate
        self.prev_yaw_rate = yaw_rate

        correction = (KP * self.heading_error +
                     KI * self.heading_integral +
                     KD * derivative)

        left_speed = clamp(self.base_speed + correction, -100, 100)
        right_speed = clamp(self.base_speed - correction, -100, 100)

        return left_speed, right_speed

    def control_callback(self):
        """Read IMU, apply PID, publish both IMU data and motor commands"""
        current_time = time.time()

        # Calibrate first
        if not self.is_calibrated:
            self.calibrate_gyro()
            return

        # Read IMU
        try:
            accel = self.imu.read_accelerometer()
            gyro = self.imu.read_gyroscope()
        except Exception as e:
            self.get_logger().error(f"Failed to read IMU: {e}")
            return

        # Apply calibration offsets
        corrected_gyro = [
            gyro[0] - self.gyro_offset[0],
            gyro[1] - self.gyro_offset[1],
            gyro[2] - self.gyro_offset[2],
        ]

        # --- Publish raw IMU data to /imu/data (for monitoring) ---
        imu_msg = String()
        imu_msg.data = json.dumps({
            'timestamp': current_time,
            'accel': {'x': float(accel[0]), 'y': float(accel[1]), 'z': float(accel[2])},
            'gyro': {'x': corrected_gyro[0], 'y': corrected_gyro[1], 'z': corrected_gyro[2]}
        })
        self.imu_publisher.publish(imu_msg)

        # --- PID control + motor command ---
        if self.prev_time is not None:
            dt = current_time - self.prev_time
            if dt > 0:
                yaw_rate = corrected_gyro[2]  # Z axis
                self.yaw_angle += yaw_rate * dt

                left_speed, right_speed = self.calculate_motor_correction(yaw_rate)

                # Publish motor command to /motor/command
                cmd_msg = String()
                cmd_msg.data = json.dumps({
                    'left_speed': left_speed,
                    'right_speed': right_speed,
                })
                self.cmd_publisher.publish(cmd_msg)

                # Check duration
                if self.duration is not None:
                    elapsed = current_time - self.start_time
                    if elapsed >= self.duration:
                        stop_msg = String()
                        stop_msg.data = json.dumps({'left_speed': 0.0, 'right_speed': 0.0})
                        self.cmd_publisher.publish(stop_msg)
                        self.get_logger().info(f"Duration {self.duration}s reached. Stopping.")
                        rclpy.shutdown()
                        return

                # Log status
                elapsed = current_time - self.start_time
                self.get_logger().info(
                    f"Heading: {self.yaw_angle:6.1f}° | Yaw: {yaw_rate:6.2f}°/s | "
                    f"Motors: L={left_speed:3.0f}% R={right_speed:3.0f}% | Time: {elapsed:5.1f}s",
                    throttle_duration_sec=0.5
                )

        self.prev_time = current_time

    def destroy_node(self):
        """Clean up — send stop command and release IMU"""
        try:
            stop_msg = String()
            stop_msg.data = json.dumps({'left_speed': 0.0, 'right_speed': 0.0})
            self.cmd_publisher.publish(stop_msg)
        except Exception:
            pass
        if hasattr(self, 'imu'):
            self.imu.cleanup()
        self.get_logger().info("IMU controller cleanup complete.")
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = None
    try:
        node = IMUControllerNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        if node:
            node.get_logger().info("\nStopping IMU controller...")
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


