#!/usr/bin/env bash
# Automated test flight against a running SITL (start run_sitl.sh first, separate terminal).
# Usage: run_test.sh [baseline|peregrine] [extra flight_test.py args]
#   baseline   model's own parameters
#   peregrine  + flight-logic parameters of ../peregrine-kakuteh7.params
# Restart the SITL between runs: parameters persist in the SITL until reset.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-baseline}"; shift || true
case "$MODE" in
  baseline)  exec python3 "$HERE/flight_test.py" "$@" ;;
  peregrine) exec python3 "$HERE/flight_test.py" --params "$HERE/../peregrine-kakuteh7.params" "$@" ;;
  *) echo "usage: $0 [baseline|peregrine] [args]"; exit 2 ;;
esac
