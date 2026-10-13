#!/usr/bin/env bash
# Install Gazebo Harmonic + simulation tools and build PX4 SITL (WSL2 Ubuntu 24.04).
# Run once after software/px4/tools/setup_wsl.sh. Asks for the sudo password.
set -euo pipefail
PX4_DIR="${PX4_DIR:-$HOME/projects/FSL/px4/PX4-Autopilot}"
cd "$PX4_DIR"

# ubuntu.sh WITHOUT --no-sim-tools adds the OSRF apt repo and installs gz-harmonic
bash Tools/setup/ubuntu.sh --no-nuttx
pip install --break-system-packages --user pymavlink pyulog

# the gz bridge is only compiled if Gazebo was found at configure time:
# drop an older SITL build that was configured without it
rm -rf build/px4_sitl_default
make px4_sitl
echo
echo "Done. Start the simulation with: $(dirname "$0")/run_sitl.sh"
