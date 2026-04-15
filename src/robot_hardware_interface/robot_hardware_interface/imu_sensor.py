"""IMU sensor module for reading 9-axis IMU data via I2C"""

import smbus2
import time
from robot_common.constants import IMU_I2C_BUS, IMU_I2C_ADDRESS


class IMUSensor:
    """Interface for 9-axis IMU (gyroscope, accelerometer, magnetometer)"""
    
    # MPU6050/MPU6886 Register addresses
    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43
    
    # Scale factors
    ACCEL_SCALE = 16384.0  # LSB/g for ±2g range
    GYRO_SCALE = 131.0      # LSB/(deg/s) for ±250 deg/s range
    
    def __init__(self, i2c_bus=IMU_I2C_BUS, i2c_address=IMU_I2C_ADDRESS):
        """
        Initialize IMU sensor
        
        Args:
            i2c_bus: I2C bus number (default 1 for Raspberry Pi)
            i2c_address: I2C address of IMU (default 0x68)
        """
        self.bus = smbus2.SMBus(i2c_bus)
        self.address = i2c_address
        self._initialize()
    
    def _initialize(self):
        """Wake up IMU and configure it"""
        try:
            # Wake up the device (clear sleep bit)
            self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)
            time.sleep(0.1)  # Wait for device to wake up
        except Exception as e:
            raise RuntimeError(f"Failed to initialize IMU: {e}")
    
    def read_accelerometer(self):
        """
        Read accelerometer data
        
        Returns:
            tuple: (accel_x, accel_y, accel_z) in g (gravitational units)
        """
        try:
            # Read 6 bytes starting from ACCEL_XOUT_H
            data = self.bus.read_i2c_block_data(self.address, self.ACCEL_XOUT_H, 6)
            
            # Combine high and low bytes for each axis
            accel_x = self._convert_to_signed_16bit(data[0], data[1]) / self.ACCEL_SCALE
            accel_y = self._convert_to_signed_16bit(data[2], data[3]) / self.ACCEL_SCALE
            accel_z = self._convert_to_signed_16bit(data[4], data[5]) / self.ACCEL_SCALE
            
            return accel_x, accel_y, accel_z
        except Exception as e:
            raise RuntimeError(f"Failed to read accelerometer: {e}")
    
    def read_gyroscope(self):
        """
        Read gyroscope data
        
        Returns:
            tuple: (gyro_x, gyro_y, gyro_z) in degrees/second
        """
        try:
            # Read 6 bytes starting from GYRO_XOUT_H
            data = self.bus.read_i2c_block_data(self.address, self.GYRO_XOUT_H, 6)
            
            # Combine high and low bytes for each axis
            gyro_x = self._convert_to_signed_16bit(data[0], data[1]) / self.GYRO_SCALE
            gyro_y = self._convert_to_signed_16bit(data[2], data[3]) / self.GYRO_SCALE
            gyro_z = self._convert_to_signed_16bit(data[4], data[5]) / self.GYRO_SCALE
            
            return gyro_x, gyro_y, gyro_z
        except Exception as e:
            raise RuntimeError(f"Failed to read gyroscope: {e}")
    
    def read_all(self):
        """
        Read all sensor data at once
        
        Returns:
            dict: Dictionary with 'accel' and 'gyro' keys containing (x, y, z) tuples
        """
        accel = self.read_accelerometer()
        gyro = self.read_gyroscope()
        
        return {
            'accelerometer': {'x': accel[0], 'y': accel[1], 'z': accel[2]},
            'gyroscope': {'x': gyro[0], 'y': gyro[1], 'z': gyro[2]}
        }
    
    @staticmethod
    def _convert_to_signed_16bit(high_byte, low_byte):
        """
        Convert two bytes to a signed 16-bit integer
        
        Args:
            high_byte: Most significant byte
            low_byte: Least significant byte
            
        Returns:
            int: Signed 16-bit value
        """
        value = (high_byte << 8) | low_byte
        if value > 32767:
            value -= 65536
        return value
    
    def cleanup(self):
        """Close I2C bus connection"""
        if self.bus:
            self.bus.close()
