#!/usr/bin/env python3
"""
Extract and plot Task 2 (IMU Straight Line Control) bagfile data

Usage:
    python3 plot_task2_data.py rosbags/task2_test3
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ matplotlib not installed. Install with: pip3 install matplotlib")
    sys.exit(1)

try:
    from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
    ROSBAG_AVAILABLE = True
except ImportError:
    ROSBAG_AVAILABLE = False
    print("⚠️ rosbag2_py not installed")


def extract_bag_data_mcap(bag_path):
    """Extract topic data from MCAP bagfile using simple file parsing"""
    
    try:
        import mcap
        print("✓ Using MCAP library")
    except ImportError as e:
        print(f"⚠️ mcap not installed: {e}")
        return None
    
    bag_path = Path(bag_path)
    mcap_file = bag_path / f"{bag_path.name}_0.mcap"
    
    if not mcap_file.exists():
        print(f"❌ MCAP file not found: {mcap_file}")
        return None
    
    print(f"✓ Reading MCAP file: {mcap_file}")
    
    imu_data = {'times': [], 'accel_x': [], 'accel_y': [], 'accel_z': [], 
                'gyro_x': [], 'gyro_y': [], 'gyro_z': []}
    motor_cmd = {'times': [], 'pwm_a': [], 'pwm_b': []}
    motor_status = {'times': [], 'speed_a': [], 'speed_b': []}
    
    try:
        # Try different mcap APIs
        try:
            # Try newer API
            from mcap.reader import iter_message_data
            with open(mcap_file, 'rb') as f:
                for message in iter_message_data(f):
                    try:
                        msg_data = json.loads(message.data.decode('utf-8'))
                        timestamp = message.publish_time / 1e9
                        
                        if message.topic == '/imu/data':
                            imu_data['times'].append(timestamp)
                            imu_data['accel_x'].append(msg_data.get('accel_x', 0))
                            imu_data['accel_y'].append(msg_data.get('accel_y', 0))
                            imu_data['accel_z'].append(msg_data.get('accel_z', 0))
                            imu_data['gyro_x'].append(msg_data.get('gyro_x', 0))
                            imu_data['gyro_y'].append(msg_data.get('gyro_y', 0))
                            imu_data['gyro_z'].append(msg_data.get('gyro_z', 0))
                        
                        elif message.topic == '/motor/command':
                            motor_cmd['times'].append(timestamp)
                            motor_cmd['pwm_a'].append(msg_data.get('cmd_pwm_a', 0))
                            motor_cmd['pwm_b'].append(msg_data.get('cmd_pwm_b', 0))
                        
                        elif message.topic == '/motor/status':
                            motor_status['times'].append(timestamp)
                            motor_status['speed_a'].append(msg_data.get('speed_a', 0))
                            motor_status['speed_b'].append(msg_data.get('speed_b', 0))
                    except:
                        pass
                        
        except ImportError:
            print("⚠️ iter_message_data not available, using fallback")
            # Simple JSON fallback - just read the file as text and find JSON blocks
            with open(mcap_file, 'rb') as f:
                content = f.read()
                # Look for JSON patterns in the file
                import re
                # Find all JSON-like structures
                json_pattern = rb'\{[^{}]*(?:"[^"]*"[^{}]*)*\}'
                for match in re.finditer(json_pattern, content):
                    try:
                        msg_str = match.group().decode('utf-8', errors='ignore')
                        msg_data = json.loads(msg_str)
                        # Assume timestamp is in ms or ns, convert to seconds
                        if 'timestamp' in msg_data:
                            timestamp = msg_data['timestamp'] / 1e9 if msg_data['timestamp'] > 1e10 else msg_data['timestamp']
                        else:
                            continue
                            
                        if 'accel_x' in msg_data:
                            imu_data['times'].append(timestamp)
                            imu_data['accel_x'].append(msg_data.get('accel_x', 0))
                            imu_data['accel_y'].append(msg_data.get('accel_y', 0))
                            imu_data['accel_z'].append(msg_data.get('accel_z', 0))
                            imu_data['gyro_x'].append(msg_data.get('gyro_x', 0))
                            imu_data['gyro_y'].append(msg_data.get('gyro_y', 0))
                            imu_data['gyro_z'].append(msg_data.get('gyro_z', 0))
                        
                        elif 'cmd_pwm_a' in msg_data:
                            motor_cmd['times'].append(timestamp)
                            motor_cmd['pwm_a'].append(msg_data.get('cmd_pwm_a', 0))
                            motor_cmd['pwm_b'].append(msg_data.get('cmd_pwm_b', 0))
                        
                        elif 'speed_a' in msg_data:
                            motor_status['times'].append(timestamp)
                            motor_status['speed_a'].append(msg_data.get('speed_a', 0))
                            motor_status['speed_b'].append(msg_data.get('speed_b', 0))
                    except:
                        pass
        
        return {
            'imu': imu_data,
            'motor_cmd': motor_cmd,
            'motor_status': motor_status
        }
        
    except Exception as e:
        print(f"❌ Error reading MCAP file: {e}")
        import traceback
        traceback.print_exc()
        return None


def extract_bag_data(bag_path):
    """Extract topic data from ROS2 bagfile (tries MCAP first, then fallback)"""
    
    # Try MCAP format (ROS2 Jazzy default)
    data = extract_bag_data_mcap(bag_path)
    if data:
        return data
    
    print("⚠️ Could not read bag file in MCAP format")
    print("   Install mcap: pip3 install mcap-protobuf")
    return None


def normalize_time(data):
    """Normalize all times to start at 0"""
    if not data:
        return data
    
    for key in data:
        if 'times' in data[key] and data[key]['times']:
            min_time = min(data[key]['times'])
            data[key]['times'] = [t - min_time for t in data[key]['times']]
    
    return data


def create_plots(data, output_file="task2_analysis.png"):
    """Create comprehensive plots of Task 2 behavior"""
    
    if not data or not any(data.values()):
        print("❌ No data to plot")
        return
    
    fig, axes = plt.subplots(3, 2, figsize=(14, 10))
    fig.suptitle('Task 2: IMU Straight Line Control System Analysis', fontsize=16, fontweight='bold')
    
    # Plot 1: Gyroscope Z-axis (Yaw rate)
    if data['imu']['times']:
        ax = axes[0, 0]
        ax.plot(data['imu']['times'], data['imu']['gyro_z'], 'b-', linewidth=2)
        ax.set_ylabel('Gyro Z (deg/s)', fontsize=10)
        ax.set_title('Yaw Rate (Gyroscope Z-axis)', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    
    # Plot 2: Motor Commands (PWM)
    if data['motor_cmd']['times']:
        ax = axes[0, 1]
        ax.plot(data['motor_cmd']['times'], data['motor_cmd']['pwm_a'], 'g-', label='Motor A (Right)', linewidth=2)
        ax.plot(data['motor_cmd']['times'], data['motor_cmd']['pwm_b'], 'b-', label='Motor B (Left)', linewidth=2)
        ax.set_ylabel('PWM Command (%)', fontsize=10)
        ax.set_title('Motor Command Output', fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
    
    # Plot 3: Accelerometer (XY plane for drift detection)
    if data['imu']['times']:
        ax = axes[1, 0]
        ax.plot(data['imu']['times'], data['imu']['accel_x'], 'r-', label='Accel X', linewidth=2)
        ax.plot(data['imu']['times'], data['imu']['accel_y'], 'g-', label='Accel Y', linewidth=2)
        ax.set_ylabel('Acceleration (m/s²)', fontsize=10)
        ax.set_title('Acceleration (X, Y)', fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
    
    # Plot 4: Motor Speeds (Actual)
    if data['motor_status']['times']:
        ax = axes[1, 1]
        ax.plot(data['motor_status']['times'], data['motor_status']['speed_a'], 'g-', label='Motor A Speed', linewidth=2)
        ax.plot(data['motor_status']['times'], data['motor_status']['speed_b'], 'b-', label='Motor B Speed', linewidth=2)
        ax.set_ylabel('Speed (%)', fontsize=10)
        ax.set_title('Actual Motor Speeds', fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
    
    # Plot 5: Motor Speed Difference (PID Effect)
    if data['motor_status']['times']:
        ax = axes[2, 0]
        speed_diff = [a - b for a, b in zip(data['motor_status']['speed_a'], data['motor_status']['speed_b'])]
        ax.plot(data['motor_status']['times'], speed_diff, 'purple', linewidth=2)
        ax.set_xlabel('Time (s)', fontsize=10)
        ax.set_ylabel('Speed Difference (%)', fontsize=10)
        ax.set_title('Motor Speed Difference (Correction Signal)', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    
    # Plot 6: System Overview (Gyro vs Motor Correction)
    if data['imu']['times'] and data['motor_status']['times']:
        ax = axes[2, 1]
        ax2 = ax.twinx()
        
        line1 = ax.plot(data['imu']['times'], data['imu']['gyro_z'], 'b-', label='Yaw Rate', linewidth=2)
        speed_diff = [a - b for a, b in zip(data['motor_status']['speed_a'], data['motor_status']['speed_b'])]
        line2 = ax2.plot(data['motor_status']['times'], speed_diff, 'g-', label='Motor Correction', linewidth=2)
        
        ax.set_xlabel('Time (s)', fontsize=10)
        ax.set_ylabel('Yaw Rate (deg/s)', color='b', fontsize=10)
        ax2.set_ylabel('Motor Correction (%)', color='g', fontsize=10)
        ax.set_title('Control System Feedback Loop', fontweight='bold')
        ax.tick_params(axis='y', labelcolor='b')
        ax2.tick_params(axis='y', labelcolor='g')
        ax.grid(True, alpha=0.3)
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Plot saved to: {output_file}")
    
    # Also display statistics
    print_statistics(data)


def print_statistics(data):
    """Print statistics about the recorded data"""
    
    print("\n" + "="*60)
    print("TASK 2 CONTROL SYSTEM STATISTICS")
    print("="*60 + "\n")
    
    if data['imu']['times']:
        print(f"IMU Data:")
        print(f"  Duration: {data['imu']['times'][-1]:.2f}s")
        print(f"  Samples: {len(data['imu']['times'])}")
        print(f"  Gyro Z range: [{min(data['imu']['gyro_z']):.2f}, {max(data['imu']['gyro_z']):.2f}] deg/s")
        print(f"  Gyro Z mean: {np.mean(data['imu']['gyro_z']):.2f} deg/s")
        print(f"  Gyro Z std: {np.std(data['imu']['gyro_z']):.2f} deg/s")
    
    if data['motor_cmd']['times']:
        print(f"\nMotor Commands:")
        print(f"  Motor A range: [{min(data['motor_cmd']['pwm_a']):.1f}, {max(data['motor_cmd']['pwm_a']):.1f}]%")
        print(f"  Motor B range: [{min(data['motor_cmd']['pwm_b']):.1f}, {max(data['motor_cmd']['pwm_b']):.1f}]%")
    
    if data['motor_status']['times']:
        print(f"\nMotor Status:")
        speed_diff = [a - b for a, b in zip(data['motor_status']['speed_a'], data['motor_status']['speed_b'])]
        print(f"  Speed A mean: {np.mean(data['motor_status']['speed_a']):.1f}%")
        print(f"  Speed B mean: {np.mean(data['motor_status']['speed_b']):.1f}%")
        print(f"  Speed difference range: [{min(speed_diff):.1f}, {max(speed_diff):.1f}]%")
        print(f"  Speed difference mean: {np.mean(speed_diff):.1f}%")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 plot_task2_data.py <bagfile_path>")
        print("Example: python3 plot_task2_data.py rosbags/task2_run")
        sys.exit(1)
    
    bag_path = sys.argv[1]
    print(f"📊 Reading bag file from: {bag_path}")
    
    data = extract_bag_data(bag_path)
    if data:
        data = normalize_time(data)
        create_plots(data, "task2_analysis.png")
        print("\n✓ Analysis complete!")
    else:
        print("❌ Failed to read bag file")
