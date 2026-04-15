"""Utility functions used across all robot packages"""

import math


def clamp(value, min_value, max_value):
    """Clamp a value between min and max bounds."""
    return max(min_value, min(value, max_value))


def map_range(value, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def calculate_angle_from_gyro(gyro_data, dt):
    """
    Calculate angle change from gyro data
    
    Args:
        gyro_data: Gyroscope reading in degrees/second
        dt: Time delta in seconds
        
    Returns:
        float: Angle change in degrees
    """
    return gyro_data * dt


def calculate_magnitude(x, y, z=0):
    """
    Calculate magnitude of 3D vector (or 2D if z=0)
    
    Args:
        x, y, z: Vector components
        
    Returns:
        float: Magnitude
    """
    return math.sqrt(x**2 + y**2 + z**2)


def line_sensor_position(sensor_array):
    """
    Calculate the position error based on line sensor readings
    Assumes sensor_array is a list of 5 boolean values [left to right]
    Returns position: -2 to 2 where 0 is center
    
    Args:
        sensor_array: List of 5 boolean sensor values
        
    Returns:
        float: Position error from -2 to 2
    """
    if len(sensor_array) != 5:
        return 0
    
    # Weight each sensor position
    weights = [-2, -1, 0, 1, 2]
    detected = sum(w for w, s in zip(weights, sensor_array) if s)
    count = sum(1 for s in sensor_array if s)
    
    if count == 0:
        return 0
    
    return detected / count

