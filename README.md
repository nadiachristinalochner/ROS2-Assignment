# Robot ROS 2 Workspace

A comprehensive ROS 2 workspace for a Raspberry Pi 4-based robot with dual DC motors, IMU sensor, line follower, and Pi Camera.

## Hardware Setup

- **Microcontroller**: Raspberry Pi 4
- **Motors**: Two DC motors with PWM control (DRV8833 drivers)
- **IMU**: 9-axis sensor (3-axis gyroscope, 3-axis accelerometer, 3-axis magnetometer)
- **Line Sensor**: Reflectance-based line follower sensor array
- **Camera**: Pi Camera for vision-based tasks
- **Encoders**: None (open-loop control for most tasks)

## Workspace Structure

### Core Packages

1. **robot_hardware_interface**
   - Low-level hardware abstraction layer
   - Motor controller module
   - IMU sensor interface
   - Provides standardized ROS 2 interfaces for hardware

2. **robot_common**
   - Shared constants and configurations
   - Utility functions
   - GPIO pin definitions
   - PID gain parameters

### Task Packages

1. **task1_motor_control**
   - Simple open-loop motor control
   - Drive robot forward at equal PWM on both motors
   - No sensor feedback

2. **task2_imu_straight_line**
   - Closed-loop control using IMU gyroscope
   - Detects unwanted rotation and corrects
   - Maintains straight driving path using PID control

3. **task3_line_follower**
   - Analog sensor-based line following
   - Uses reflectance sensors for line detection
   - Proportional control for steering

4. **task4_vision_line_follower**
   - Camera-based line following
   - OpenCV image processing
   - HSV color-space thresholding for line detection
   - Most computationally intensive but most flexible

## Building the Workspace

### Prerequisites

```bash
sudo apt update
sudo apt install python3-colcon-common-extensions python3-rosdep
```

### Build Steps

```bash
cd ~/demo1
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Running Tasks

### Task 1: Motor Control
```bash
ros2 launch task1_motor_control motor_control.launch.py
```

### Task 2: IMU Straight Line
```bash
ros2 launch task2_imu_straight_line imu_control.launch.py
```

### Task 3: Line Follower
```bash
ros2 launch task3_line_follower line_follower.launch.py
```

### Task 4: Vision Line Follower
```bash
ros2 launch task4_vision_line_follower vision_control.launch.py
```

## Development Notes

- All nodes are initially placeholders
- Implement nodes following the stub structure provided
- Use ROS 2 standard message types (Twist for velocity, Imu for sensor data)
- Ensure nodes subscribe to and publish on standard topics:
  - `/cmd_vel` - velocity commands
  - `/imu/data` - IMU data
  - `/line_sensors` - line sensor data
  - `/camera/image_raw` - camera frames

## GPIO Configuration

See `robot_common/constants.py` for pin definitions:
- Motor A (Left): GPIO 21, 20
- Motor B (Right): GPIO 18, 16
- PWM Frequency: 100 Hz

## Testing

Run individual nodes for testing:
```bash
ros2 run task1_motor_control motor_node
ros2 run task2_imu_straight_line imu_controller_node
ros2 run task3_line_follower line_sensor_node
ros2 run task4_vision_line_follower vision_node
```

## License

Apache 2.0

## Author

Raspberry Pi Robot Development Team
