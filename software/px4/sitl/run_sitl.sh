#!/usr/bin/env bash
# Start PX4 SITL.  Usage: run_sitl.sh [model] [--headless]
#   model: gz_quadtailsitter (default, Gazebo quad tail-sitter without control surfaces)
#          sihsim_standard_vtol, sihsim_quadx, sihsim_xvert (no Gazebo needed)
# The PX4 shell stays in this terminal (pxh>). Run flight_test.py in a second terminal.
set -euo pipefail
PX4_DIR="${PX4_DIR:-$HOME/projects/FSL/px4/PX4-Autopilot}"
MODEL="${1:-gz_quadtailsitter}"
[ "${2:-}" = "--headless" ] && export HEADLESS=1
cd "$PX4_DIR"
make px4_sitl "$MODEL"
