"""Inter-process communication utilities for robot coordination"""

import json
import time
from dataclasses import dataclass
from typing import Optional
from multiprocessing import Manager, Queue


@dataclass
class IMUData:
    """Container for IMU sensor data"""
    timestamp: float
    accel_x: float
    accel_y: float
    accel_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    
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


class IMUDataQueue:
    """Thread-safe queue for passing IMU data between processes"""
    
    def __init__(self, queue=None):
        """Initialize the queue
        
        Args:
            queue: Shared multiprocessing queue (if None, creates new one)
        """
        self.queue = queue
    
    def put(self, imu_data: IMUData, block=True, timeout=None):
        """Put IMU data in queue"""
        if self.queue is None:
            return
        self.queue.put(imu_data, block=block, timeout=timeout)
    
    def get(self, block=True, timeout=None) -> Optional[IMUData]:
        """Get IMU data from queue"""
        if self.queue is None:
            return None
        try:
            return self.queue.get(block=block, timeout=timeout)
        except Exception as e:
            # Catch all queue empty exceptions (queue.Empty, _queue.Empty, etc.)
            if 'Empty' in type(e).__name__:
                return None
            # Re-raise other exceptions
            raise
    
    def empty(self) -> bool:
        """Check if queue is empty"""
        if self.queue is None:
            return True
        try:
            return self.queue.empty()
        except:
            return True
    
    def qsize(self) -> int:
        """Get queue size"""
        if self.queue is None:
            return 0
        try:
            return self.queue.qsize()
        except:
            return 0


# Global queue for IPC (will be set by launcher)
imu_data_queue = IMUDataQueue()

