#!/bin/bash

# Setup script for ROS 2 Robot Workspace
# This script initializes the environment and builds the workspace

set -e

echo "================================"
echo "ROS 2 Robot Workspace Setup"
echo "================================"

# Check if ROS 2 is installed
if [ ! -d "/opt/ros" ]; then
    echo "Error: ROS 2 is not installed. Please install ROS 2 first."
    echo "Visit: https://docs.ros.org/en/humble/Installation.html"
    exit 1
fi

# Source ROS 2 setup
echo "Sourcing ROS 2 setup..."
source /opt/ros/humble/setup.bash

# Navigate to workspace
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORKSPACE_DIR"

# Install dependencies
echo "Installing Python dependencies..."
pip3 install --user colcon-common-extensions

# Build workspace
echo "Building workspace..."
colcon build --symlink-install

# Source the built workspace
echo "Sourcing workspace..."
source install/setup.bash

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "To use this workspace, run:"
echo "  cd $WORKSPACE_DIR"
echo "  source install/setup.bash"
echo ""
echo "Available launch files:"
echo "  ros2 launch robot_hardware_interface hardware.launch.py"
echo "  ros2 launch task1_motor_control motor_control.launch.py"
echo "  ros2 launch task2_imu_straight_line imu_control.launch.py"
echo "  ros2 launch task3_line_follower line_follower.launch.py"
echo "  ros2 launch task4_vision_line_follower vision_control.launch.py"
echo ""
