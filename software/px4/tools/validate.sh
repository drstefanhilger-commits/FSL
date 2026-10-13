#!/usr/bin/env bash
# Validate the Peregrine .params files against a PX4 build.
# Usage: validate.sh [PX4_DIR] [BUILD_TARGET]
#   PX4_DIR       default: ~/projects/FSL/px4/PX4-Autopilot
#   BUILD_TARGET  default: holybro_kakuteh7_peregrine (must be built first)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PX4_DIR="${1:-$HOME/projects/FSL/px4/PX4-Autopilot}"
TARGET="${2:-holybro_kakuteh7_peregrine}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

echo "== 1/2: against the firmware metadata of build/$TARGET"
python3 -I "$HERE/fw_paramdb.py" "$PX4_DIR/build/$TARGET/parameters.json" "$TMP/fw.json"
python3 -I "$HERE/check_params.py" "$TMP/fw.json" "$HERE"/../*.params | grep -v '^ok' || true

echo "== 2/2: against all parameter definitions in the PX4 source tree"
python3 -I "$HERE/px4_paramdb.py" "$PX4_DIR/src" "$TMP/src.json"
python3 -I "$HERE/check_params.py" "$TMP/src.json" "$HERE"/../*.params | grep -v '^ok'
