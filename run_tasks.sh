#!/bin/bash
# Robot control launcher - Choose which task to run

# Check if running as root (needed for GPIO)
if [ "$EUID" -ne 0 ]; then
    echo "GPIO access required. Re-running with sudo..."
    sudo bash "$0" "$@"
    exit $?
fi

source /opt/ros/jazzy/setup.bash
source install/setup.bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Display menu
clear
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    ROBOT CONTROL SYSTEM                         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Select a control mode:${NC}"
echo ""
echo -e "${GREEN}1)${NC} Task 1 — Pure Motor Control"
echo "   → Both motors at equal PWM, no sensor feedback"
echo ""
echo -e "${GREEN}2)${NC} Task 2 — IMU Straight Line"
echo "   → Drive forward in a straight line using IMU feedback"
echo ""
echo -e "${GREEN}3)${NC} Task 3 — Line Following"
echo "   → Follow a line using the 5-channel line sensor"
echo ""
echo -e "${GREEN}q)${NC} Quit"
echo ""
read -p "Enter your choice (1-3 or q): " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}Starting Task 1: Pure Motor Control${NC}"
        echo "Both motors at equal speed, no sensor feedback"
        echo "Press Ctrl+C to stop"
        echo ""

        # Start shared motor controller in background
        bash -c 'source /opt/ros/jazzy/setup.bash && source install/setup.bash && python3 src/task1_motor_control/task1_motor_control/nodes/motor_controller_node.py' &
        MOTOR_PID=$!
        sleep 2

        # Start basic commander in foreground
        python3 src/task1_motor_control/task1_motor_control/nodes/basic_motor_node.py "$@"

        kill $MOTOR_PID 2>/dev/null
        wait $MOTOR_PID 2>/dev/null
        echo -e "${GREEN}✓ Done${NC}"
        ;;
    2)
        echo ""
        echo -e "${YELLOW}Starting Task 2: IMU Straight Line Control${NC}"
        echo "Starting motor controller and IMU controller..."
        echo "Press Ctrl+C to stop"
        echo ""

        # Start shared motor controller in background
        bash -c 'source /opt/ros/jazzy/setup.bash && source install/setup.bash && python3 src/task1_motor_control/task1_motor_control/nodes/motor_controller_node.py' &
        MOTOR_PID=$!
        sleep 2

        # Start IMU controller (reads IMU + PID + publishes /motor/command) in foreground
        python3 src/task2_imu_straight_line/task2_imu_straight_line/nodes/imu_controller_node.py "$@"

        kill $MOTOR_PID 2>/dev/null
        wait $MOTOR_PID 2>/dev/null
        echo -e "${GREEN}✓ Done${NC}"
        ;;
    3)
        echo ""
        echo -e "${YELLOW}Starting Task 3: Line Following${NC}"
        echo "Starting line sensor publisher and motor controller..."
        echo "Press Ctrl+C to stop"
        echo ""

        # Start line sensor publisher in background
        bash -c 'source /opt/ros/jazzy/setup.bash && source install/setup.bash && python3 src/task3_line_follower/task3_line_follower/nodes/line_sensor_publisher_node.py' &
        SENSOR_PID=$!
        sleep 2

        # Start line follower motor controller in foreground
        python3 src/task3_line_follower/task3_line_follower/nodes/line_follower_motor_node.py "$@"

        kill $SENSOR_PID 2>/dev/null
        wait $SENSOR_PID 2>/dev/null
        echo -e "${GREEN}✓ Done${NC}"
        ;;
    q|Q)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice. Please try again.${NC}"
        exit 1
        ;;
esac
