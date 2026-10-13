# ArduPilot → PX4 migration notes

This page records how the original ArduPlane configuration (`software/ardupilot/peregrine-kakuteh7.param`) was carried over to PX4 v1.17, what had to change on the bench, and what PX4 does differently. Every PX4 parameter name, type and range used in `software/px4/*.params` was checked against the PX4 v1.17.0 source; the values are still **starter values, not flight-tested**.

## What changes on the aircraft

| Area | ArduPilot | PX4 | Action |
|---|---|---|---|
| **GPS UART** | UART3 (T3/R3 pads), `SERIAL3_PROTOCOL 5` | UART3 is the PX4 **system console**; GPS1 is **UART4** (T4/R4) | **Move the GPS TX/RX wires from T3/R3 to R4/T4** (GPS TX → R4, GPS RX → T4). 5 V, GND, SCL, SDA stay. |
| **Body frame / orientation** | Fixed-wing attitude (nose forward). `AHRS_ORIENTATION 0` | **Hover attitude** (nose up). `SENS_BOARD_ROT 24` (Pitch 90°) for the same mounting | Calibrate accelerometer and level horizon **standing on the spikes**, not lying nose-forward. |
| **OSD** | `OSD_TYPE 5` (MSP DisplayPort), in the stock firmware | `msp_osd` driver, **not in the stock `holybro_kakuteh7` build** | Build/flash `holybro_kakuteh7_peregrine` (one-line board variant in `software/px4/board/`). |
| **Bootloader** | ArduPilot `.apj`/`.hex` via DFU | PX4 bootloader must be flashed once via DFU, then PX4 firmware via QGC | See SETUP.md §1. |
| **ESC configuration** | BLHeli/AM32 passthrough (`SERVO_BLH_AUTO 1`) | **No ESC passthrough in PX4** | Reverse motors with the DShot spin-direction command in QGC → Actuators, or configure the ESC before flashing PX4. |
| **Ground station** | Mission Planner or QGC | **QGroundControl only** | — |
| **IMU** | MPU6000, ICM-42688-P and BMI270 probed | The `holybro_kakuteh7` target probes MPU6000 (v1.3 and older) and ICM-42688-P (v1.5, current), **not BMI270** | Nothing for normal boards. Only if a board with a BMI270 shows no IMU: copy `software/px4/sdcard/etc/extras.txt` to the SD card. |

## Parameter mapping

| ArduPilot | Value | PX4 | Value | Notes |
|---|---|---|---|---|
| `Q_ENABLE` | 1 | Airframe *Generic VTOL Tailsitter* (`SYS_AUTOSTART 13200`) | — | Pick it in QGC → Airframe first; it resets all parameters. |
| `Q_FRAME_CLASS` / `Q_FRAME_TYPE` | 1 / 1 (Quad X) | `CA_ROTOR_COUNT` + `CA_ROTORn_PX/PY/KM` | 4, ±0.134 m, ±0.05 | Same motor numbering and spin directions as ArduPilot Quad X. |
| `Q_TAILSIT_ENABLE` | 2 (no control surfaces) | `VT_TYPE 0`, `CA_AIRFRAME 4`, `CA_SV_CS_COUNT 0`, `MAV_TYPE 20` | — | — |
| (implicit: motors fly FW) | — | `VT_FW_DIFTHR_EN` | 7 | Yaw + roll + pitch by differential thrust in forward flight. Scales `VT_FW_DIFTHR_S_R/P/Y` = 1.0/1.0/0.3. |
| `Q_TAILSIT_ANGLE` | 45° | *(fixed in PX4: 60°)* | — | PX4 ends the forward transition below −60° pitch **and** above `VT_ARSP_TRANS` (if airspeed is used). Not configurable. |
| — | — | `VT_F_TRANS_DUR` / `VT_B_TRANS_DUR` | 2.5 s / 2.0 s | Pitch rate = 90° / duration. Close to ArduPilot's default 50°/s tail-sitter rates. |
| `ARSPD_TYPE` | 1 | `SENS_EN_MS4525DO` | 1 | External I2C. |
| `ARSPD_USE` | 0 (stage 1) → 1 | `FW_USE_AIRSPD` (+ `SYS_HAS_NUM_ASPD`) | 0 → 1 | Stage 2 is the separate `peregrine-kakuteh7-airspeed.params`. |
| `AIRSPEED_MIN` / `_CRUISE` / `_MAX` | 18 / 30 / 56 | `FW_AIRSPD_MIN` / `_TRIM` / `_MAX` | 18 / 30 / 56 | Plus `FW_AIRSPD_STALL 15` (must be ≤ MIN). |
| `Q_TAILSIT_GSCMSK 4`, `_DSKLD 12`, `_GSCMIN 0.3`, `_GSCMAX 2` | — | `FW_ARSP_SCALE_EN 1` + `FW_AIRSPD_TRIM` | 1, 30 | PX4 scales FW rate output by (TRIM/airspeed)². At 56 m/s: 0.29 (≈ GSCMIN 0.3). Below trim it goes up to (30/15)² = 4 at stall speed, where ArduPilot capped at 2. **No disk-loading model**, see below. |
| `Q_M_PWM_TYPE` | 6 (DShot600) | `PWM_MAIN_TIM0`, `PWM_MAIN_TIM1` | −3 | Timer groups: M1/M2 = 0, M3/M4 = 1. |
| `SERVO1..4_FUNCTION` | 33..36 | `PWM_MAIN_FUNC1..4` | 101..104 | Motor 1..4. |
| `SERVO_BLH_AUTO`, `SERVO_DSHOT_ESC` | 1, 1 | — | — | No passthrough; DShot commands work out of the box. |
| `SERIAL7_PROTOCOL 16`, `SERVO_BLH_TRATE 10` | ESC telemetry | *(started by the board on UART7)* | — | Nothing to set; `MOT_POLE_COUNT 14` for RPM. |
| `Q_M_SPIN_ARM` | 0.08 | `DSHOT_MIN` | 0.08 | Armed idle. |
| `Q_M_SPIN_MIN` | 0.12 | `MPC_THR_MIN` | 0.12 | Minimum collective in assisted hover modes. |
| `Q_M_THST_HOVER` | 0.35 | `MPC_THR_HOVER` | 0.35 | The hover thrust estimator refines it in flight. |
| `SERIAL3_PROTOCOL 5`, `GPS_TYPE 2` | UART3 | `GPS_1_CONFIG` | 201 (GPS1 = UART4) | **Rewire**, see above. `SYS_HAS_MAG 1` (board default is 0). |
| `SERIAL6_PROTOCOL 23`, `RSSI_TYPE 3` | CRSF | `RC_INPUT_PROTO` | 6 (CRSF) | UART6 is PX4's RC port; link quality and telemetry come with CRSF. |
| `SERIAL1_PROTOCOL 42`, `SERIAL1_BAUD 115`, `OSD_TYPE 5`, `OSD1_TXT_RES 1` | MSP DisplayPort | `MSP_OSD_CONFIG 101` (TELEM1 = UART1), `MAV_0_CONFIG 0` | — | 115200 baud is fixed in the driver. QGC connects over USB. Layout via `OSD_SYMBOLS`. |
| `BATT_MONITOR 4` | analog V+I | `BAT1_SOURCE 0` | 0 | Dividers from board defaults (`BAT1_V_DIV 11.2`, `BAT1_A_PER_V 59.5`): calibrate. |
| `BATT_CAPACITY` | 2200 | `BAT1_CAPACITY`, `BAT1_N_CELLS` | 2200, 6 | — |
| `BATT_LOW_VOLT` / `BATT_CRT_VOLT` | 21.0 / 19.8 V | `BAT1_V_EMPTY 3.5`, `BAT_LOW_THR 0.20`, `BAT_CRIT_THR 0.10` | — | PX4 uses state of charge, not fixed voltages. |
| (battery failsafe action, default "none") | — | `COM_LOW_BAT_ACT` | 3 | **Behaviour change:** Return at critical, Land at emergency. Set 0 for warning-only like before. |
| `THR_FAILSAFE 1`, `FS_LONG_ACTN 1` | RC loss → RTL | `NAV_RCL_ACT` | 2 (Return) | `COM_RC_LOSS_T` default 0.5 s. |

### Flight modes

| ArduPlane | PX4 (VTOL) |
|---|---|
| QSTABILIZE | Stabilized (hover) |
| QHOVER | Altitude (hover) |
| QLOITER | Position (hover) |
| FBWA | Stabilized **after** the transition switch is set to fixed-wing |
| FBWB / CRUISE | Altitude / Position in fixed-wing |
| QRTL | Return (in forward flight: returns as a plane, back-transitions and lands in hover; in hover: returns as a multicopter) |
| QAUTOTUNE | QGC → PID Tuning → Autotune (`MC_AT_EN 1` in hover; the fixed-wing autotune is started from the same button while in forward flight) |

The parameter file assumes ExpressLRS channel order: CH5 arm (`RC_MAP_ARM_SW`), CH6 mode switch (`RC_MAP_FLTMODE`, slots Stabilized / Altitude / Position / Hold / Return / Land), CH7 transition (`RC_MAP_TRANS_SW`).

## Behaviour that differs and needs attention in flight test

1. **Gain scaling is a dynamic-pressure model, not a prop-inflow model.** ArduPilot's disk-theory mode (`Q_TAILSIT_GSCMSK 4` + `Q_TAILSIT_DSKLD`) estimates the air over the props. PX4 only uses (TRIM/airspeed)², which was designed for control surfaces. The high-speed end comes out similar (0.29 vs 0.3), but motor authority at speed is not modelled. If the FW axes oscillate at speed, lower `VT_FW_DIFTHR_S_*` or `FW_*R_P`; if they are sluggish, raise them. Do not fly above about 25 m/s before stage 2 (`FW_USE_AIRSPD 1`), because without airspeed the scaling stays at 1.
2. **Motors can stop in forward flight.** PX4's tail-sitter allocator stops a motor whose command drops below 2 % in FW mode. With differential thrust on all axes that removes control. `FW_THR_MIN 0.15` protects the assisted FW modes (Altitude, Position, Return, Mission); in FW **Stabilized** the throttle stick is passed straight through, so never close the throttle fully there (an EdgeTX throttle curve with a 15–20 % floor in the FW flight mode is a good guard).
3. **Forward-flight roll is the weakest axis.** In forward flight roll comes only from the props' reaction torque (`CA_ROTORn_KM`), the same physics as in ArduPilot. Tune it first and expect lower roll rates than pitch/yaw.
4. **Transition end condition.** PX4 completes the forward transition at −60° pitch plus `VT_ARSP_TRANS` (18 m/s) when airspeed is in use, instead of ArduPilot's 45° angle. `VT_TRANS_TIMEOUT 10` aborts it back to hover if it does not complete.
5. **Calibration attitude.** Everything is in the hover frame. A board calibrated nose-forward (ArduPilot habit) will show a 90° wrong horizon. Check in QGC that tilting the nose towards the belly side shows pitch-forward in hover.

## Not carried over

- `MSP_OPTIONS 0`, `OSD1_TXT_RES 1`: no PX4 equivalent. PX4's `msp_osd` has a fixed element layout; positions are not configurable per element.
- `SERVO_BLH_TRATE`: telemetry rate is fixed by the PX4 DShot driver.
- ArduPilot logs (`.bin`) and Mission Planner tuning tools: PX4 writes `.ulg` logs to the SD card; analyse them with [Flight Review](https://review.px4.io) or PlotJuggler.
