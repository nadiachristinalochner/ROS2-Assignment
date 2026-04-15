#!/bin/bash
# Run motor + IMU straight line control in one terminal

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "This script requires GPIO access. Re-running with sudo..."
    sudo bash "$0" "$@"
    exit $?
fi

source /opt/ros/jazzy/setup.bash
source install/setup.bash

# Color codes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🤖 ROBOT STRAIGHT LINE CONTROL (IMU-Based)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Starting Motor Controller (background)...${NC}"

# Start shared motor controller in background
bash -c 'source /opt/ros/jazzy/setup.bash && source install/setup.bash && python3 src/task1_motor_control/task1_motor_control/nodes/motor_controller_node.py' &
MOTOR_PID=$!

# Give motor controller time to initialize
sleep 2

echo -e "${YELLOW}Starting IMU Controller...${NC}"
echo ""

# Start IMU controller (reads IMU + PID + publishes /motor/command) in foreground
python3 src/task2_imu_straight_line/task2_imu_straight_line/nodes/imu_controller_node.py "$@"

# Cleanup: kill motor controller when IMU controller exits
echo ""
echo -e "${YELLOW}Stopping Motor Controller...${NC}"
kill $MOTOR_PID 2>/dev/null
wait $MOTOR_PID 2>/dev/null

echo -e "${GREEN}✓ Done${NC}"
