#!/usr/bin/env python3
"""
Task 2 Plot Generator - Reads ROS2 bag files and creates plots
"""

import sys
import json
import numpy as np
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("❌ matplotlib not installed: pip3 install matplotlib")
    sys.exit(1)

try:
    from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
    print("✓ rosbag2_py available")
except ImportError:
    print("❌ rosbag2_py not available")
    sys.exit(1)


def read_bagfile(bag_path):
    """Read bag file using rosbag2_py"""
    
    bag_path = Path(bag_path)
    
    data = {
        'imu': {'times': [], 'accel_x': [], 'accel_y': [], 'accel_z': [], 
                'gyro_x': [], 'gyro_y': [], 'gyro_z': []},
        'motor_cmd': {'times': [], 'pwm_a': [], 'pwm_b': []},
        'motor_status': {'times': [], 'speed_a': [], 'speed_b': []}
    }
    
    try:
        storage_options = StorageOptions(uri=str(bag_path), storage_id='mcap')
        converter_options = ConverterOptions()
        
        reader = SequentialReader()
        reader.open(storage_options, converter_options)
        
        msg_count = 0
        import re
        while reader.has_next():
            try:
                topic, msg_bytes, timestamp = reader.read_next()
                msg_count += 1
                
                # Debug: show first few messages
                if msg_count <= 2:
                    print(f"  Message {msg_count}: topic={topic}, bytes_len={len(msg_bytes)}, first 100 bytes: {msg_bytes[:100]}")
                
                # Try to extract JSON from binary CDR message
                try:
                    # Look for JSON pattern in the binary data
                    json_match = re.search(rb'\{[^}]*\}', msg_bytes)
                    if json_match:
                        msg_str = json_match.group().decode('utf-8')
                        msg_data = json.loads(msg_str)
                        ts = timestamp / 1e9  # nanoseconds to seconds
                        
                        if topic == '/imu/data':
                            data['imu']['times'].append(ts)
                            data['imu']['accel_x'].append(float(msg_data.get('accel_x', 0)))
                            data['imu']['accel_y'].append(float(msg_data.get('accel_y', 0)))
                            data['imu']['accel_z'].append(float(msg_data.get('accel_z', 0)))
                            data['imu']['gyro_x'].append(float(msg_data.get('gyro_x', 0)))
                            data['imu']['gyro_y'].append(float(msg_data.get('gyro_y', 0)))
                            data['imu']['gyro_z'].append(float(msg_data.get('gyro_z', 0)))
                        
                        elif topic == '/motor/command':
                            data['motor_cmd']['times'].append(ts)
                            data['motor_cmd']['pwm_a'].append(float(msg_data.get('cmd_pwm_a', 0)))
                            data['motor_cmd']['pwm_b'].append(float(msg_data.get('cmd_pwm_b', 0)))
                        
                        elif topic == '/motor/status':
                            data['motor_status']['times'].append(ts)
                            data['motor_status']['speed_a'].append(float(msg_data.get('speed_a', 0)))
                            data['motor_status']['speed_b'].append(float(msg_data.get('speed_b', 0)))
                except:
                    pass
            except:
                break
        
        print(f"✓ Read {msg_count} messages")
        print(f"  IMU points: {len(data['imu']['times'])}")
        print(f"  Motor cmd points: {len(data['motor_cmd']['times'])}")
        print(f"  Motor status points: {len(data['motor_status']['times'])}")
        
        return data
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def plot_data(data, output_file="task2_analysis.png"):
    """Create plots from extracted data"""
    
    if not data or not any(len(v['times']) > 0 for v in data.values()):
        print("❌ No data to plot")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Task 2: IMU Straight Line Control', fontsize=16, fontweight='bold')
    
    # Plot 1: Gyro Z (Yaw rate)
    ax = axes[0, 0]
    if data['imu']['times']:
        ax.plot(np.array(data['imu']['times']) - data['imu']['times'][0], 
                data['imu']['gyro_z'], 'b-', linewidth=2)
        ax.set_ylabel('Gyro Z (deg/s)', fontsize=10)
        ax.set_title('Yaw Rate', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    
    # Plot 2: Motor Commands
    ax = axes[0, 1]
    if data['motor_cmd']['times']:
        times_norm = np.array(data['motor_cmd']['times']) - data['motor_cmd']['times'][0]
        ax.plot(times_norm, data['motor_cmd']['pwm_a'], 'g-', label='A (Right)', linewidth=2)
        ax.plot(times_norm, data['motor_cmd']['pwm_b'], 'b-', label='B (Left)', linewidth=2)
        ax.set_ylabel('PWM (%)', fontsize=10)
        ax.set_title('Motor Commands', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # Plot 3: Accelerometer
    ax = axes[1, 0]
    if data['imu']['times']:
        times_norm = np.array(data['imu']['times']) - data['imu']['times'][0]
        ax.plot(times_norm, data['imu']['accel_x'], 'r-', label='Accel X', linewidth=2)
        ax.plot(times_norm, data['imu']['accel_y'], 'g-', label='Accel Y', linewidth=2)
        ax.set_ylabel('Accel (m/s²)', fontsize=10)
        ax.set_title('Acceleration', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # Plot 4: Motor Speed Difference
    ax = axes[1, 1]
    if data['motor_status']['times']:
        times_norm = np.array(data['motor_status']['times']) - data['motor_status']['times'][0]
        speed_diff = np.array(data['motor_status']['speed_a']) - np.array(data['motor_status']['speed_b'])
        ax.plot(times_norm, speed_diff, 'purple', linewidth=2)
        ax.set_xlabel('Time (s)', fontsize=10)
        ax.set_ylabel('Speed Diff (%)', fontsize=10)
        ax.set_title('Motor Correction (A - B)', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Plot saved to: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 plot_task2_v2.py <bagfile_path>")
        print("Example: python3 plot_task2_v2.py rosbags/task2_test3")
        sys.exit(1)
    
    bag_path = sys.argv[1]
    print(f"📊 Reading: {bag_path}")
    
    data = read_bagfile(bag_path)
    if data:
        plot_data(data)
        print("✓ Done!")
    else:
        print("❌ Failed to read bag file")
