#!/usr/bin/env python3
"""Line sensor node for Task 3 - Digital Sensor-Based Line Following with ROS2

This node reads digital sensor data from the 5-channel line following sensor array
and implements proportional control to follow a line. Uses ROS2 rclpy for node management.
"""

import RPi.GPIO as GPIO
import time
import rclpy
from rclpy.node import Node
from robot_hardware_interface import MotorController
from robot_common import line_sensor_position, clamp
from robot_common.constants import (
    LINE_SENSOR_PINS,
    KP, KI, KD
)


class LineSensorNode(Node):
    """Node for reading line sensors and controlling motor movement"""
    
    def __init__(self):
        """Initialize line sensors and motor controller"""
        super().__init__('line_sensor_node')
        
        self.motor_controller = MotorController()
        self.line_pins = LINE_SENSOR_PINS
        self._setup_sensors()
        
        # Declare parameters
        self.declare_parameter('base_speed', 50)
        self.declare_parameter('loop_rate', 20)  # Hz
        
        # Get parameters
        self.base_speed = self.get_parameter('base_speed').value
        loop_rate = self.get_parameter('loop_rate').value
        
        # PID state
        self.prev_error = 0
        self.integral = 0
        
        # Create timer for control loop
        self.loop_period = 1.0 / loop_rate
        self.create_timer(self.loop_period, self.control_loop_callback)
        
        self.get_logger().info(f"Line sensor node initialized with base speed {self.base_speed}%")
    
    def _setup_sensors(self):
        """Configure GPIO pins for line sensors"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        for pin in self.line_pins:
            GPIO.setup(pin, GPIO.IN)
    
    def read_line_sensors(self):
        """
        Read all line sensors
        
        Returns:
            list: Boolean values for each sensor (True = line detected)
        """
        return [GPIO.input(pin) for pin in self.line_pins]
    
    def calculate_motor_speeds(self, sensor_data):
        """
        Calculate motor speeds using proportional control
        
        Args:
            sensor_data: Line sensor readings
            
        Returns:
            tuple: (motor_a_speed, motor_b_speed)
        """
        # Get line position error (0 = centered, -2 to +2 = offset)
        position_error = line_sensor_position(sensor_data)
        
        # Calculate PID correction
        self.integral += position_error
        derivative = position_error - self.prev_error
        
        correction = (KP * position_error + 
                     KI * self.integral + 
                     KD * derivative)
        
        self.prev_error = position_error
        
        # Apply correction to motor speeds
        motor_a_speed = clamp(self.base_speed - correction, -100, 100)
        motor_b_speed = clamp(self.base_speed + correction, -100, 100)
        
        return motor_a_speed, motor_b_speed
    
    def control_loop_callback(self):
        """Timer callback for control loop"""
        try:
            # Read sensor data
            sensor_data = self.read_line_sensors()
            
            # Calculate motor speeds
            speed_a, speed_b = self.calculate_motor_speeds(sensor_data)
            
            # Set motor speeds
            self.motor_controller.set_motor_speeds(speed_a, speed_b)
            
            # Log debug info
            sensor_str = ''.join(['#' if s else '-' for s in sensor_data])
            self.get_logger().debug(f"Sensors: {sensor_str} | Speeds: A={speed_a:3.0f} B={speed_b:3.0f}")
        
        except Exception as e:
            self.get_logger().error(f"Error in control loop: {e}")
    
    def destroy_node(self):
        """Clean up resources"""
        self.motor_controller.stop()
        self.motor_controller.cleanup()
        GPIO.cleanup()
        self.get_logger().info("Line sensor node cleanup complete.")
        super().destroy_node()


def main(args=None):
    """Main entry point"""
    rclpy.init(args=args)
    
    node = LineSensorNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down line sensor node...")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

