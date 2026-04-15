"""Constants used across all robot packages"""

# Motor Driver (Pololu DRV8833) - GPIO Pin Configuration (BCM numbering)
# Motor A (Right motor)
MOTOR_A_IN1 = 21  # AIN1
MOTOR_A_IN2 = 20  # AIN2
# Motor B (Left motor)
MOTOR_B_IN1 = 24  # BIN1
MOTOR_B_IN2 = 23  # BIN2

# I2C Configuration for IMU
IMU_I2C_BUS = 1  # Standard I2C bus on Raspberry Pi
IMU_I2C_ADDRESS = 0x68  # Default address for MPU6050/MPU6886
IMU_SDA_PIN = 2  # GPIO 2
IMU_SCL_PIN = 3  # GPIO 3

# Line Sensor Configuration (5-channel digital sensors)
LINE_SENSOR_OUT1_PIN = 16  # GPIO 16
LINE_SENSOR_OUT2_PIN = 22  # GPIO 22
LINE_SENSOR_OUT3_PIN = 26  # GPIO 26
LINE_SENSOR_OUT4_PIN = 27  # GPIO 27
LINE_SENSOR_OUT5_PIN = 25  # GPIO 25
LINE_SENSOR_COUNT = 5  # Number of line sensors
LINE_SENSOR_PINS = [
    LINE_SENSOR_OUT1_PIN,
    LINE_SENSOR_OUT2_PIN,
    LINE_SENSOR_OUT3_PIN,
    LINE_SENSOR_OUT4_PIN,
    LINE_SENSOR_OUT5_PIN,
]

# PWM Configuration for Motor Speed Control
PWM_FREQUENCY = 100  # Hz
PWM_PIN_MOTOR_A = MOTOR_A_IN1  # PWM on motor A control pin
PWM_PIN_MOTOR_B = MOTOR_B_IN1  # PWM on motor B control pin

# Motor Control Limits
MIN_PWM_DUTY = 0.0
MAX_PWM_DUTY = 100.0

# PID Control Gains (for Task 2 - IMU straight line)
KP = 1.0  # Proportional gain
KI = 0.1  # Integral gain
KD = 0.05  # Derivative gain

# PID Control Gains (for Task 3 - Line following)
LINE_KP = 8.0    # Proportional gain (position error range: -2 to 2)
LINE_KI = 0.0    # Integral gain (start with 0 to avoid overshoot)
LINE_KD = 3.0    # Derivative gain (dampen oscillation)

# Camera Configuration (for Task 4)
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
CAMERA_FPS = 30
