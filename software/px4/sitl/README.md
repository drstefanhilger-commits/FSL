# PX4 SITL (software-in-the-loop)

Simulates PX4 v1.17 with the **Gazebo quad tail-sitter** (`gz_quadtailsitter`, airframe 4018). It is the closest PX4 model to Peregrine: four motors, no control surfaces, forward flight on differential thrust (`VT_FW_DIFTHR_EN 7`), airspeed sensor.

> **It is not Peregrine.** Mass (1.6 kg), geometry (rotors at ±0.15/±0.23 m), propellers and aerodynamics are the model's own. Use it to check the *logic*: mode switching, transitions, failsafes, the test procedure, and how the Peregrine transition/differential-thrust parameters behave. Do not copy tuning results from it to the aircraft.

| File | Purpose |
|---|---|
| `setup_gz.sh` | Once: installs Gazebo Harmonic (via PX4's `ubuntu.sh`, asks for sudo) and builds `px4_sitl` with the Gazebo bridge. |
| `run_sitl.sh` | Starts the simulation. Default `gz_quadtailsitter`; `--headless` without Gazebo GUI. Also `sihsim_*` models (no Gazebo). |
| `flight_test.py` | Automated flight: arm → takeoff 30 m → transition to FW → loiter → back-transition → land. Prints per-phase altitude, airspeed and attitude spread, `PASS`/`FAIL`. |
| `run_test.sh` | `baseline` (model's parameters) or `peregrine` (+ flight-logic subset of `../peregrine-kakuteh7.params`). |

## Use (WSL2 Ubuntu 24.04, after `../tools/setup_wsl.sh`)

```sh
~/projects/FSL/fsl/software/px4/sitl/setup_gz.sh          # once

# terminal 1
~/projects/FSL/fsl/software/px4/sitl/run_sitl.sh           # Gazebo window via WSLg
# terminal 2
~/projects/FSL/fsl/software/px4/sitl/run_test.sh baseline
# stop the SITL (Ctrl+C / "shutdown" in pxh>), start again, then:
~/projects/FSL/fsl/software/px4/sitl/run_test.sh peregrine
```

Parameters persist inside the SITL. For a clean baseline, delete `build/px4_sitl_default/rootfs/parameters*.bson` before starting.

### What `peregrine` applies

Only the flight-logic parameters: `VT_FW_DIFTHR_*`, `VT_*_TRANS_*`, `VT_ARSP_*`, `FW_THR_MIN`, `FW_ARSP_SCALE_EN`, `MPC_THR_MIN`, failsafes (`NAV_RCL_ACT`, `NAV_DLL_ACT`, `COM_LOW_BAT_ACT`), `MC_AT_EN`. Skipped: outputs, serial ports, sensors, battery, geometry (`CA_*`), vehicle type, hover thrust, airspeed sensor settings. `FW_AIRSPD_*` (18/30/56 m/s) are also skipped because the simulated airframe only flies 14–22 m/s; force them with `run_test.sh peregrine --include-airspeeds` to see what happens.

Note: `VT_ARSP_TRANS 18` is close to this model's trim speed (18 m/s); if the forward transition times out in the `peregrine` run, that is the reason, not a fault in the logic.

### QGroundControl on Windows

PX4 SITL sends MAVLink to `localhost:14550`. With WSL's **mirrored networking** QGC on Windows connects automatically: add to `%UserProfile%\.wslconfig`

```ini
[wsl2]
networkingMode=mirrored
```

and run `wsl --shutdown` once. Without it, type `param set MAV_0_BROADCAST 1` in `pxh>` instead.

## Checks done

- `flight_test.py` was run end to end against PX4 v1.17.0 SITL with `sihsim_standard_vtol` (Gazebo is not installable in the cloud environment it was written in): arm, takeoff, transition to FW (3.1 s), 30 s loiter, back-transition, landing → `PASS`. Parameter import and read-back (INT32 and REAL32) verified.
- **Not yet run against `gz_quadtailsitter`** – that is the first thing to do with these scripts.
- `sihsim_xvert` (PX4's SIH duo tail-sitter) tips over on the ground at takeoff in v1.17.0 with its stock parameters; use the Gazebo model instead.
