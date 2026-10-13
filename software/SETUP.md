# Software setup

Every piece of software here is open source or free, and none of it is written for this airframe. The project-specific files are the PX4 parameter files and a one-line PX4 board variant in [`px4/`](px4).

| Layer | Software | Licence | What it does here |
|-------|----------|---------|-------------------|
| Flight controller firmware | [PX4 Autopilot](https://px4.io/) v1.17, target `holybro_kakuteh7` (custom variant `holybro_kakuteh7_peregrine`) | BSD-3-Clause | Motor-only tail-sitter: hovers like a quad, transitions nose-forward like a plane |
| Ground control | [QGroundControl](https://qgroundcontrol.com/) | Apache-2.0 / GPLv3 | Flashing, airframe, parameters, calibration, actuator test, tuning |
| ESC firmware | BLHeli_32 or AM32 (factory on the Tekko32) | AM32 is GPLv3 | DShot600 + telemetry, no changes needed |
| Radio link | [ExpressLRS](https://www.expresslrs.org/) + [EdgeTX](https://edgetx.org/) on the transmitter | GPLv3 | CRSF RC link and telemetry |
| Video | HDZero firmware (VTX + goggles) | vendor | Digital video, MSP DisplayPort OSD |
| Log analysis | [Flight Review](https://review.px4.io) or [PlotJuggler](https://plotjuggler.io/) | BSD / MPL-2.0 | `.ulg` logs from the SD card |

> Moving over from ArduPilot? Read [`px4/MIGRATION.md`](px4/MIGRATION.md) first. Two things change on the bench: **the GPS moves from UART3 to UART4**, and **all calibration is done in the hover attitude**.

## 1. Flash the flight controller

The Kakute H7 ships with Betaflight. PX4 needs its own bootloader once.

1. **PX4 bootloader.** Hold the boot button, plug in USB-C, and flash [`holybro_kakuteh7_bootloader.hex`](https://github.com/PX4/PX4-Autopilot/raw/main/docs/assets/flight_controller/kakuteh7/holybro_kakuteh7_bootloader.hex) in DFU mode (Betaflight Configurator or `dfu-util`), as described in the PX4 guide [Bootloader update from Betaflight](https://docs.px4.io/main/en/advanced_config/bootloader_update_from_betaflight.html).
2. **Firmware.** Build the Peregrine variant (it adds the HDZero OSD driver; see [`px4/README.md`](px4/README.md)), then in QGC go to *Vehicle Setup → Firmware*, unplug/replug, choose *PX4 Pro → Advanced → Custom firmware file* and select `holybro_kakuteh7_peregrine.px4`.
   Without the custom build you can flash the stock *PX4 Pro stable* for `holybro_kakuteh7`; everything works except the OSD.
3. **Airframe.** *Vehicle Setup → Airframe → VTOL Tailsitter → Generic VTOL Tailsitter*, *Apply and Restart*. This resets all parameters.
4. **Parameters.** *Parameters → Tools → Load from file…* → [`px4/peregrine-kakuteh7.params`](px4/peregrine-kakuteh7.params), then reboot. QGC reports any parameter it cannot find (on the stock firmware that is `MSP_OSD_CONFIG`).
5. **SD card.** Fit a microSD card (FAT32): PX4 logs to it. The PX4 target finds the MPU6000 (v1.3 and older) and the ICM-42688-P (v1.5, current). Only if QGC reports **no accelerometer/gyro** and your board carries a **BMI270**, copy [`px4/sdcard/etc/extras.txt`](px4/sdcard/etc/extras.txt) to `/etc/extras.txt` on the card.

## 2. Orientation and calibration: do these in the HOVER attitude

PX4 defines a tail-sitter's body frame in the **hover attitude**: nose up, standing on the four spikes. This is the opposite of ArduPilot. In that frame "forward" (+X) is the **belly** side of the aircraft in forward flight, "right" (+Y) is the right wing, "down" (+Z) is towards the tail.

- **Board orientation** (`SENS_BOARD_ROT`, *Sensors → Set orientations*). The stack lies flat on the tray. The parameter file sets **24 (Pitch 90°)** for the default mounting: FC arrow pointing at the **nose**, component side towards the **top** of the aircraft. Other mountings:

  | FC arrow points to | Component side | `SENS_BOARD_ROT` |
  |---|---|---|
  | nose | top | 24 (Pitch 90°) |
  | right wing | top | 18 (Roll 90°, Yaw 90°) |
  | tail | top | 34 (Roll 180°, Pitch 270°) |
  | left wing | top | 36 (Roll 90°, Pitch 180°, Yaw 90°) |
  | nose | bottom | 29 (Roll 180°, Pitch 90°) |

  Leave the compass orientation on the GPS at its default unless the calibration says otherwise.
- **Check before calibrating:** stand the aircraft on its spikes; the QGC horizon must be level. Tip the nose towards the belly side: QGC must show pitch **down** (forward). Roll it towards the right wing: roll **right**.
- **Accelerometer** (6 positions): QGC's pictures show a quadcopter; "level" means standing on the spikes, "nose down" means the belly side down, and so on.
- **Level horizon**: standing on the spikes, on a level floor.
- **Compass**: with the battery fitted and the GPS screwed into the nose.
- **Airspeed**: *Sensors → Airspeed* with the pitot covered from wind (calibrates `SENS_DPRES_OFF`).
- **Battery**: *Power → Battery 1*: measure pack voltage and current once and use the calculators to set `BAT1_V_DIV` and `BAT1_A_PER_V`.

## 3. Motors (props OFF)

- PX4 numbers motors like ArduPilot's Quad X, viewed from above **in hover** (from the nose, looking aft): **1** front-right CCW, **2** rear-left CCW, **3** front-left CW, **4** rear-right CW, where "front" is the belly side.
- *Vehicle Setup → Actuators*: the geometry from the parameter file is shown at the top. Use the **motor sliders** (props off!) to check each motor's position, then *Identify & Assign Motors* if the order is wrong.
- **Spin direction:** reverse a motor with the *Set Spin Direction* buttons on the same page (DShot command, stored in the ESC). PX4 has **no BLHeli/AM32 passthrough**; to change other ESC settings, do it before flashing PX4 or with a separate USB-to-signal adapter.
- Outputs are DShot600 (`PWM_MAIN_TIM0/1 = -3`). ESC telemetry on UART7 is started automatically.

## 4. Radio (ExpressLRS)

- Flash the RX and TX with the same ELRS major version and binding phrase (ExpressLRS Configurator).
- RX wiring: RX-TX → **R6**, RX-RX → **T6**, 5 V, GND. UART6 is PX4's RC port; `RC_INPUT_PROTO = 6` (CRSF) is in the parameter file, and telemetry back to the radio works automatically.
- Channel plan in the parameter file (change it to match your model, then run *Radio* calibration):
  - **CH5** arm switch (`RC_MAP_ARM_SW`), the ELRS AUX1 channel.
  - **CH6** 6-position mode switch (`RC_MAP_FLTMODE`): Stabilized, Altitude, Position, Hold, Return, Land.
  - **CH7** VTOL transition switch (`RC_MAP_TRANS_SW`): low = hover, high = forward flight.
- Mode equivalents: QSTABILIZE = Stabilized, QHOVER = Altitude, QLOITER = Position, QRTL = Return. **FBWA = Stabilized with the transition switch in forward flight**.

## 5. Video and OSD (HDZero)

- The VTX plugs into the FC's HD/VTX port (9 V + GND + UART1). In PX4 UART1 is `TELEM1`.
- The parameter file sets `MSP_OSD_CONFIG = 101` (TELEM1) and `MAV_0_CONFIG = 0`, so MAVLink no longer uses TELEM1; QGC connects over USB. The driver talks MSP DisplayPort at a fixed 115200 baud.
- Choose the elements with `OSD_SYMBOLS` (bitmask). PX4's OSD layout is fixed; the per-element positions and the HD text resolution of ArduPilot (`OSD1_TXT_RES`) have no equivalent.
- If your VTX connector is wired to another UART, change `MSP_OSD_CONFIG` to that port (UART6 is taken by the receiver, UART4 by the GPS).

## 6. First flights

1. **Bench:** props off, arm in Stabilized, check that every stick moves the right motors (*Actuators* page shows the outputs).
2. **Hover:** tethered or low hover in Stabilized, then run the multicopter autotune (*PID Tuning → Autotune*, `MC_AT_EN = 1`) in Altitude mode.
3. **Position** mode once GPS and compass are healthy.
4. **Transition:** only after a stable hover, at 30 m+, flip the transition switch to forward flight in **Altitude** mode (keeps `FW_THR_MIN`), with a quick switch back to hover. PX4 pitches down at 90°/`VT_F_TRANS_DUR` (2.5 s) and completes at −60° pitch; `VT_TRANS_TIMEOUT` (10 s) falls back to hover. In forward-flight **Stabilized** never close the throttle fully: the motors are the only control effectors and PX4 stops a motor commanded below 2 % (use an EdgeTX throttle floor).
5. **Going fast (target 200 km/h / 56 m/s):** fit the airspeed sensor, calibrate it, check that it reads sensibly (blow on the pitot), then load [`px4/peregrine-kakuteh7-airspeed.params`](px4/peregrine-kakuteh7-airspeed.params) (`FW_USE_AIRSPD = 1`). Only then go above about 25 m/s: PX4 reduces the forward-flight gains as (`FW_AIRSPD_TRIM`/airspeed)². Raise speed in steps (25 → 35 → 45 → 56 m/s). If it oscillates at speed, lower `VT_FW_DIFTHR_S_R/P/Y` or the FW rate gains; the fixed-wing autotune can be run in forward flight. Swap 7×5 props for 7×6 only once hover and transitions are solid.

Always follow your local aviation rules (registration, line-of-sight/FPV spotter rules, no-fly zones).
