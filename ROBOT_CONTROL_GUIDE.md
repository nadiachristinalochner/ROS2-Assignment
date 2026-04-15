## 🤖 Robot Control System Guide

Your robot is now set up to run three different control methods:

---

## **Quick Start**

Option 1: **Use the interactive launcher** (easiest)
```bash
cd /home/pi/demo1
./run_tasks.sh
```

Option 2: **Run commands directly** (see below)

---

## **TASK 1: Basic Motor Control (No IMU)**

**Purpose:** Drive both motors at equal speed forward without any feedback

**Command (Single Terminal):**
```bash
cd /home/pi/demo1
source /opt/ros/jazzy/setup.bash
source install/setup.bash
python3 src/task1_motor_control/task1_motor_control/nodes/motor_node.py --no-imu
```

**Expected Output:**
```
✓ Motor controller initialized
============================================================
MODE: Basic motor control (no IMU)
============================================================
Base speed: 50%
Duration: Infinite (press Ctrl+C to stop)
🤖 Driving forward at 50% speed
```

**Parameters:**
- `--no-imu` flag: Run without waiting for IMU
- Adjust speed via: `-p base_speed:=75` (0-100%)
- Set duration: `-p duration:=10` (seconds, -1 = infinite)

**Example with parameters:**
```bash
python3 src/task1_motor_control/task1_motor_control/nodes/motor_node.py --no-imu -p base_speed:=70 -p duration:=5
```

---

## **TASK 2: IMU Data Publisher**

**Purpose:** Read real IMU sensor and publish data for other nodes to consume

**Command (Single Terminal):**
```bash
cd /home/pi/demo1
source /opt/ros/jazzy/setup.bash
source install/setup.bash
python3 src/task2_imu_straight_line/task2_imu_straight_line/nodes/imu_controller_node.py
```

**Expected Output:**
```
✓ IMU initialized successfully
============================================================
Calibrating gyroscope offsets...
Calibrating: 12% [████░░░░░░░░░░░░░░░░░░░░░]
Calibrating: 99% [████████████████████████░░]
✓ Calibration complete!
Gyro offsets: X=0.0123, Y=-0.0045, Z=0.0012 deg/s
Publishing IMU data to /imu/data topic
```

**What it does:**
1. Initializes real IMU hardware
2. Calibrates gyroscope (measures & removes bias)
3. Publishes IMU data ~20 times per second to `/imu/data` topic

**Monitor data in another terminal:**
```bash
ros2 topic echo /imu/data
```

---

## **TASK 3: Motor + IMU (Straight Line Driving) ⭐ RECOMMENDED**

**Purpose:** Drive robot forward in a straight line using IMU feedback to correct motor speeds

**Requirements:** TWO TERMINALS (or use `run_tasks.sh`)

### **Terminal 1 - Start IMU Publisher:**
```bash
cd /home/pi/demo1
source /opt/ros/jazzy/setup.bash
source install/setup.bash
python3 src/task2_imu_straight_line/task2_imu_straight_line/nodes/imu_controller_node.py
```

### **Terminal 2 - Start Motor Controller (waits for IMU):**
```bash
cd /home/pi/demo1
source /opt/ros/jazzy/setup.bash
source install/setup.bash
python3 src/task1_motor_control/task1_motor_control/nodes/motor_node.py
```

**Expected Output - Terminal 1 (IMU):**
```
✓ IMU initialized successfully
Calibrating: 100%
✓ Calibration complete!
Gyro offsets: X=0.0123, Y=-0.0045, Z=0.0012 deg/s
Publishing IMU data to /imu/data topic
```

**Expected Output - Terminal 2 (Motors):**
```
✓ Motor controller initialized
============================================================
MODE: IMU-based straight line control
============================================================
Base speed: 50%
Waiting for IMU data from /imu/data topic...
✓ Connected to IMU! Starting motor control...
Heading: 0.1° | Yaw: 0.02°/s | Motors: A= 50% B= 50% | Time:  0.1s
Heading: 1.2° | Yaw: 0.15°/s | Motors: A= 51% B= 49% | Time:  0.2s
Heading: 2.3° | Yaw: 0.22°/s | Motors: A= 52% B= 48% | Time:  0.3s
```

**What's happening:**
- Task 2 reads real IMU sensor and publishes `accel` & `gyro` data
- Task 1 subscribes to `/imu/data` and detects rotation (yaw rate)
- PID controller adjusts motor speeds to minimize rotation
- Result: Robot drives forward in a straight line

**Adjust behavior:**
```bash
# Terminal 2: Higher speed, 30 second duration
python3 src/task1_motor_control/task1_motor_control/nodes/motor_node.py \
  -p base_speed:=70 -p duration:=30
```

**Monitor on a third terminal:**
```bash
ros2 topic echo /imu/data
```

---

## **Understanding the Data Flow**

```
┌─────────────────────────────────────────────────────────────┐
│ REAL IMU HARDWARE                                           │
│ (MPU6050/MPU6886 on I2C)                                    │
└────────────────┬────────────────────────────────────────────┘
                 │ reads
                 ▼
    ┌─────────────────────────────────┐
    │ TASK 2: IMU Publisher Node      │
    │ (imu_controller_node.py)        │
    │ - Calibrates gyroscope          │
    │ - Reads accelerometer/gyroscope │
    │ - Publishes JSON + timestamp    │
    └──────────────┬──────────────────┘
                   │ publishes to
                   │ /imu/data topic
                   ▼
    ┌─────────────────────────────────────────┐
    │ ROS2 Middleware (std_msgs/String)      │
    └──────────────┬──────────────────────────┘
                   │ subscribes
                   ▼
    ┌──────────────────────────────────┐
    │ TASK 1: Motor Controller Node    │
    │ (motor_node.py)                  │
    │ - Reads IMU yaw rate             │
    │ - Applies PID control            │
    │ - Adjusts motor speeds           │
    └──────────────┬───────────────────┘
                   │ commands
                   ▼
    ┌──────────────────────────────────┐
    │ REAL MOTOR HARDWARE              │
    │ (Pololu DRV8833 Motor Driver)    │
    └──────────────────────────────────┘
```

---

## **System Architecture**

### **Files Modified:**
- `src/task1_motor_control/nodes/motor_node.py` - Motor controller with `--no-imu` option
- `src/task2_imu_straight_line/nodes/imu_controller_node.py` - IMU publisher

### **ROS2 Structure:**
- **Node 1:** `IMUPublisherNode` (Task 2) - Publisher on `/imu/data`
- **Node 2:** `MotorControllerNode` (Task 1) - Subscriber to `/imu/data`
- **Communication:** `std_msgs/String` with JSON payload
- **Topic:** `/imu/data` - Contains timestamp + accel(x,y,z) + gyro(x,y,z)

### **Control Algorithm (PID):**
```
Error = Yaw Rate from IMU
Correction = KP * Error + KI * Integral(Error) + KD * dError/dt
Motor_A_Speed = Base_Speed + Correction
Motor_B_Speed = Base_Speed - Correction
```

**Constants** (in `src/robot_common/constants.py`):
- KP = 1.0 (Proportional gain)
- KI = 0.1 (Integral gain)
- KD = 0.05 (Derivative gain)

---

## **Common Issues & Solutions**

### **"✗ Failed to initialize IMU hardware"**
- Ensure IMU is connected via I2C
- Check: `i2cdetect -y 1` should show device at 0x68
- Make sure running as root or with appropriate permissions

### **"✗ Failed to initialize motor controller"**
- Ensure motor driver is connected
- Check GPIO pins in `constants.py` match your setup

### **Motor not moving in Task 1 only**
- This is correct! `--no-imu` mode just energizes motors (you'll see "🤖 Driving forward at 50% speed")
- For actual motion, run with IMU feedback (Task 3)

### **Task 1 waits forever for IMU**
- This is normal! Remove `--no-imu` and start Task 2
- Or add timeout: `timeout 10 python3 ...` to kill after 10 seconds

### **IMU readings look wrong**
- Let calibration finish (100%)
- Ensure IMU board is stationary during calibration
- Check I2C address: `i2cdetect -y 1`

---

## **Next Steps: Add Task 3 (Line Follower)**

When ready, you can add line-following sensor support by running:
```bash
python3 src/task3_line_follower/task3_line_follower/nodes/line_sensor_node.py
```

This will allow the robot to follow black lines autonomously!

---

## **Troubleshooting Commands**

```bash
# Check ROS2 topics running
ros2 topic list

# Monitor specific topic
ros2 topic echo /imu/data

# Check node info
ros2 node list
ros2 node info /motor_controller_node

# Kill all ROS processes
pkill -f rclpy
```

---

## **Summary**

✅ **Setup Complete!** Your robot now has:
- **Task 1**: Basic motor control (no sensors)
- **Task 2**: IMU sensor publishing
- **Task 3**: Straight-line driving with IMU feedback

Run `./run_tasks.sh` to get started! 🚀
