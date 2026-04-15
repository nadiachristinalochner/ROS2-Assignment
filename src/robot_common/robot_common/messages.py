"""ROS 2 compatible message definitions for robot_common"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class IMUData:
    """IMU sensor data message
    
    Contains accelerometer and gyroscope readings from the IMU sensor
    """
    timestamp: float  # Unix timestamp in seconds
    accel_x: float    # Acceleration in X axis (m/s²)
    accel_y: float    # Acceleration in Y axis (m/s²)
    accel_z: float    # Acceleration in Z axis (m/s²)
    gyro_x: float     # Angular velocity around X axis (deg/s)
    gyro_y: float     # Angular velocity around Y axis (deg/s)
    gyro_z: float     # Angular velocity around Z axis (deg/s)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'accel': {'x': self.accel_x, 'y': self.accel_y, 'z': self.accel_z},
            'gyro': {'x': self.gyro_x, 'y': self.gyro_y, 'z': self.gyro_z}
        }
    
    @staticmethod
    def from_dict(data):
        """Create from dictionary"""
        return IMUData(
            timestamp=data['timestamp'],
            accel_x=data['accel']['x'],
            accel_y=data['accel']['y'],
            accel_z=data['accel']['z'],
            gyro_x=data['gyro']['x'],
            gyro_y=data['gyro']['y'],
            gyro_z=data['gyro']['z']
        )
