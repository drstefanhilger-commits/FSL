# PX4 configuration for Peregrine

Target: **PX4 v1.17**, Holybro **Kakute H7** (v1.x, `holybro_kakuteh7`) + Tekko32 F4 4-in-1.

| File | What it is |
|---|---|
| [`peregrine-kakuteh7.params`](peregrine-kakuteh7.params) | Main parameter file (QGC format): quad tail-sitter without control surfaces, motors, DShot, GPS, CRSF, OSD, battery, failsafes, modes. Airspeed sensor fitted but **not** used yet. |
| [`peregrine-kakuteh7-airspeed.params`](peregrine-kakuteh7-airspeed.params) | Stage 2: use the airspeed sensor for gain scaling and transitions. Load only after it reads sensibly. |
| [`board/peregrine.px4board`](board/peregrine.px4board) | PX4 board variant = stock `holybro_kakuteh7` + the `msp_osd` driver for the HDZero OSD. |
| [`sdcard/etc/extras.txt`](sdcard/etc/extras.txt) | Only for a Kakute H7 with a BMI270 gyro (not the current v1.5). |
| [`firmware/`](firmware) | Prebuilt `holybro_kakuteh7_peregrine.px4` (PX4 v1.17.0 + OSD). |
| [`MIGRATION.md`](MIGRATION.md) | ArduPilot → PX4 parameter mapping, hardware changes and behaviour differences. |

The step-by-step setup is in [`../SETUP.md`](../SETUP.md).

## Building the firmware

The stock `holybro_kakuteh7` firmware has no MSP OSD driver. The variant adds exactly one line (`CONFIG_DRIVERS_OSD_MSP_OSD=y`).

```sh
git clone --recursive --branch v1.17.0 https://github.com/PX4/PX4-Autopilot.git
cd PX4-Autopilot
bash ./Tools/setup/ubuntu.sh --no-sim-tools        # toolchain, once
cp /path/to/peregrine-vtol/software/px4/board/peregrine.px4board boards/holybro/kakuteh7/
make holybro_kakuteh7_peregrine
# -> build/holybro_kakuteh7_peregrine/holybro_kakuteh7_peregrine.px4
```

Flash the `.px4` with QGC (*Firmware → Advanced → Custom firmware file*), or with the board connected over USB:

```sh
make holybro_kakuteh7_peregrine upload
```

The PX4 bootloader must already be on the board (see SETUP.md §1).

## Checks done on these files

- Every parameter name, type (INT32/REAL32), range, enum value and bitmask in both `.params` files was checked against the PX4 v1.17.0 source.
- The board variant was compiled with `make holybro_kakuteh7_peregrine` on PX4 v1.17.0.
- Not done: flight tests, SITL of this exact airframe. Treat all tuning values as starting points.
