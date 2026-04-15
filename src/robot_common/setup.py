from setuptools import setup
import os
from glob import glob

package_name = 'robot_common'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'msg'),
            glob(os.path.join('msg', '*.msg'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Raspberry Pi Robot',
    author_email='pi@raspberry.local',
    maintainer='Raspberry Pi Robot',
    maintainer_email='pi@raspberry.local',
    description='Common constants, messages, and utilities shared across all robot packages',
    license='Apache-2.0',
)
