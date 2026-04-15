from setuptools import setup
import os
from glob import glob

package_name = 'task2_imu_straight_line'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name, f'{package_name}.nodes'],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*launch.py'))),
    ],
    install_requires=['setuptools'],
    entry_points={
        'console_scripts': [
            'imu_controller_node = task2_imu_straight_line.nodes.imu_controller_node:main',
        ],
    },
    zip_safe=True,
    author='Raspberry Pi Robot',
    author_email='pi@raspberry.local',
    maintainer='Raspberry Pi Robot',
    maintainer_email='pi@raspberry.local',
    description='IMU-based straight line driving with gyroscope feedback using ROS2 topics',
    license='Apache-2.0',
)
