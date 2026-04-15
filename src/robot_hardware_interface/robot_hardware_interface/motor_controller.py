"""Motor controller module for Pololu DRV8833 motor driver"""

import RPi.GPIO as GPIO
import time
from robot_common.constants import (
    MOTOR_A_IN1, MOTOR_A_IN2,
    MOTOR_B_IN1, MOTOR_B_IN2,
    PWM_FREQUENCY, MAX_PWM_DUTY, MIN_PWM_DUTY
)


class MotorController:
    """Controls two motors using Pololu DRV8833 driver with PWM speed control"""
    
    def __init__(self):
        """Initialize motor controller and GPIO"""
        self.motor_a_in1_pwm = None
        self.motor_a_in2_pwm = None
        self.motor_b_in1_pwm = None
        self.motor_b_in2_pwm = None
        self._setup_gpio()
    
    def _setup_gpio(self):
        """Configure GPIO pins for motor control"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Motor A pins
        GPIO.setup(MOTOR_A_IN1, GPIO.OUT)
        GPIO.setup(MOTOR_A_IN2, GPIO.OUT)
        
        # Motor B pins
        GPIO.setup(MOTOR_B_IN1, GPIO.OUT)
        GPIO.setup(MOTOR_B_IN2, GPIO.OUT)
        
        # Initialize PWM on all 4 pins for proper H-bridge control
        # Forward: IN1=PWM, IN2=0
        # Backward: IN1=0, IN2=PWM
        self.motor_a_in1_pwm = GPIO.PWM(MOTOR_A_IN1, PWM_FREQUENCY)
        self.motor_a_in2_pwm = GPIO.PWM(MOTOR_A_IN2, PWM_FREQUENCY)
        self.motor_b_in1_pwm = GPIO.PWM(MOTOR_B_IN1, PWM_FREQUENCY)
        self.motor_b_in2_pwm = GPIO.PWM(MOTOR_B_IN2, PWM_FREQUENCY)
        
        # Start all PWM at 0% duty cycle
        self.motor_a_in1_pwm.start(0)
        self.motor_a_in2_pwm.start(0)
        self.motor_b_in1_pwm.start(0)
        self.motor_b_in2_pwm.start(0)
    
    def set_motor_a_speed(self, speed):
        """
        Set speed for motor A (right motor)
        
        Args:
            speed: Motor speed from -100 to 100
                   Negative = backward, Positive = forward
        """
        speed = max(-100, min(100, speed))  # Clamp to -100 to 100
        
        if speed > 0:
            # Forward: IN1=PWM, IN2=0
            self.motor_a_in1_pwm.ChangeDutyCycle(speed)
            self.motor_a_in2_pwm.ChangeDutyCycle(0)
        elif speed < 0:
            # Backward: IN1=0, IN2=PWM
            self.motor_a_in1_pwm.ChangeDutyCycle(0)
            self.motor_a_in2_pwm.ChangeDutyCycle(abs(speed))
        else:
            # Stop (coast)
            self.motor_a_in1_pwm.ChangeDutyCycle(0)
            self.motor_a_in2_pwm.ChangeDutyCycle(0)
    
    def set_motor_b_speed(self, speed):
        """
        Set speed for motor B (left motor)
        
        Args:
            speed: Motor speed from -100 to 100
                   Negative = backward, Positive = forward
        """
        speed = max(-100, min(100, speed))  # Clamp to -100 to 100
        
        if speed > 0:
            # Forward: IN1=PWM, IN2=0
            self.motor_b_in1_pwm.ChangeDutyCycle(speed)
            self.motor_b_in2_pwm.ChangeDutyCycle(0)
        elif speed < 0:
            # Backward: IN1=0, IN2=PWM
            self.motor_b_in1_pwm.ChangeDutyCycle(0)
            self.motor_b_in2_pwm.ChangeDutyCycle(abs(speed))
        else:
            # Stop (coast)
            self.motor_b_in1_pwm.ChangeDutyCycle(0)
            self.motor_b_in2_pwm.ChangeDutyCycle(0)
    
    def set_motor_speeds(self, speed_a, speed_b):
        """
        Set speeds for both motors simultaneously
        
        Args:
            speed_a: Motor A speed from -100 to 100
            speed_b: Motor B speed from -100 to 100
        """
        self.set_motor_a_speed(speed_a)
        self.set_motor_b_speed(speed_b)
    
    def stop(self):
        """Stop both motors by coasting (PWM = 0)"""
        self.set_motor_speeds(0, 0)
    
    def brake(self):
        """Brake both motors (set both pins to 100% for strong braking)"""
        self.motor_a_in1_pwm.ChangeDutyCycle(100)
        self.motor_a_in2_pwm.ChangeDutyCycle(100)
        self.motor_b_in1_pwm.ChangeDutyCycle(100)
        self.motor_b_in2_pwm.ChangeDutyCycle(100)
    
    def cleanup(self):
        """Clean up GPIO and PWM"""
        if self.motor_a_in1_pwm:
            self.motor_a_in1_pwm.stop()
        if self.motor_a_in2_pwm:
            self.motor_a_in2_pwm.stop()
        if self.motor_b_in1_pwm:
            self.motor_b_in1_pwm.stop()
        if self.motor_b_in2_pwm:
            self.motor_b_in2_pwm.stop()
        GPIO.cleanup()
