#!/usr/bin/env bash
# One-time setup of ~/projects/FSL on WSL2 Ubuntu 24.04:
#   fsl/                (this repo)   px4/PX4-Autopilot (v1.17.0)   logs/   out/
# The board variant is symlinked from this repo into the PX4 tree.
set -euo pipefail
ROOT="${FSL_ROOT:-$HOME/projects/FSL}"
PX4_TAG="${PX4_TAG:-v1.17.0}"
mkdir -p "$ROOT"/{px4,logs,out}
cd "$ROOT"

[ -d fsl/.git ] || git clone https://github.com/drstefanhilger-commits/FSL.git fsl

if [ ! -d px4/PX4-Autopilot/.git ]; then
    git clone --recursive --branch "$PX4_TAG" https://github.com/PX4/PX4-Autopilot.git px4/PX4-Autopilot
fi

# toolchain (arm-none-eabi-gcc, Python deps), no simulators
bash px4/PX4-Autopilot/Tools/setup/ubuntu.sh --no-sim-tools

ln -sfn "$ROOT/fsl/software/px4/board/peregrine.px4board" \
        "$ROOT/px4/PX4-Autopilot/boards/holybro/kakuteh7/peregrine.px4board"

cat <<MSG

Done. Next:
  cd $ROOT/px4/PX4-Autopilot && make holybro_kakuteh7_peregrine
  $ROOT/fsl/software/px4/tools/validate.sh
Log out and back in (or restart WSL) once, so the group changes from ubuntu.sh apply.
MSG
