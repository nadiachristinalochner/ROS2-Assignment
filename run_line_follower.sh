#!/bin/bash
# Run line following control in one terminal

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
echo -e "${GREEN}🤖 LINE FOLLOWING CONTROL${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Starting Line Sensor Publisher (background)...${NC}"

# Start line sensor publisher in background
bash -c 'source /opt/ros/jazzy/setup.bash && source install/setup.bash && python3 src/task3_line_follower/task3_line_follower/nodes/line_sensor_publisher_node.py' &
SENSOR_PID=$!

# Give sensors time to initialize
sleep 2

echo -e "${YELLOW}Starting Line Follower Motor Controller...${NC}"
echo ""

# Start line follower motor controller in foreground
python3 src/task3_line_follower/task3_line_follower/nodes/line_follower_motor_node.py "$@"

# Cleanup
echo ""
echo -e "${YELLOW}Stopping Line Sensor Publisher...${NC}"
kill $SENSOR_PID 2>/dev/null
wait $SENSOR_PID 2>/dev/null

echo -e "${GREEN}✓ Done${NC}"
