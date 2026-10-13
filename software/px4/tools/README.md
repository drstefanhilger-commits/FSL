# Parameter checks

Checks every line of `../*.params` (name, INT32/REAL32 type, min/max, enum value, bitmask) against PX4.

| Script | Purpose |
|---|---|
| `setup_wsl.sh` | One-time setup of `~/projects/FSL` on WSL2 Ubuntu 24.04 (clones this repo and PX4 v1.17.0, installs the toolchain, links the board variant). |
| `validate.sh` | Runs both checks below for a built PX4 tree. Default paths match `~/projects/FSL/px4/PX4-Autopilot` and target `holybro_kakuteh7_peregrine`. |
| `fw_paramdb.py` | Reads `build/<target>/parameters.json` = the parameters that **really exist in that firmware** (strictest check; it caught `EKF2_FUSE_BETA`, which is compiled out on the Kakute H7). |
| `px4_paramdb.py` | Scans the whole PX4 `src/` tree (`PARAM_DEFINE_*`, `*.yaml`). Works without a build, but cannot know what a board compiles out. Needs PyYAML. |
| `check_params.py` | Compares `.params` files with a DB from either script. Exit code 1 on any error. |

```sh
cd ~/projects/FSL/px4/PX4-Autopilot && make holybro_kakuteh7_peregrine
~/projects/FSL/fsl/software/px4/tools/validate.sh
```

Output lists only problems; `ERRORS: 0` twice means both files are clean. If the two checks disagree, **check 1 (firmware metadata) is authoritative**: the source scan merges parameters that are defined differently for different boards (e.g. `PWM_MAIN_TIMx` in `pwm_out` with DShot and in `px4io` without) and is therefore deliberately lenient.
