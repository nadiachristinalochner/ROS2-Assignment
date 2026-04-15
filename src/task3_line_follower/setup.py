from setuptools import setup
import os
from glob import glob

package_name = 'task3_line_follower'

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
            'line_sensor_node = task3_line_follower.nodes.line_sensor_node:main',
            'line_sensor_publisher_node = task3_line_follower.nodes.line_sensor_publisher_node:main',
            'line_follower_motor_node = task3_line_follower.nodes.line_follower_motor_node:main',
        ],
    },
    zip_safe=True,
    author='Raspberry Pi Robot',
    author_email='pi@raspberry.local',
    maintainer='Raspberry Pi Robot',
    maintainer_email='pi@raspberry.local',
    description='Line follower using digital reflectance sensors',
    license='Apache-2.0',
)
