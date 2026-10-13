# Prebuilt firmware

`holybro_kakuteh7_peregrine.px4` = PX4 **v1.17.0** (tag), target `holybro_kakuteh7` + [`../board/peregrine.px4board`](../board/peregrine.px4board) (adds the `msp_osd` HDZero OSD driver). Built with `make holybro_kakuteh7_peregrine`, arm-none-eabi-gcc 13.2.rel1. Flash use 96.6 %.

SHA-256: `a9acbd8e389d4e1ff004f46fa3627c496030bca34c84e2b4663825f9c47f0a0b`

Flash with QGroundControl: *Vehicle Setup → Firmware → PX4 Pro → Advanced → Custom firmware file*. The PX4 bootloader must be on the board first (see `../../SETUP.md` §1). Not flight-tested.

## Licences of the firmware binary

`holybro_kakuteh7_peregrine.px4` is **not** covered by this repository's GPL-3.0 or CC BY-SA terms. It is a build of third-party open-source software and is redistributed under the licences of its components; their full texts (including the NuttX NOTICE files required by Apache-2.0) are in [`licenses/`](licenses).

| Component | Version / source | Licence | Text |
|---|---|---|---|
| PX4 Autopilot | v1.17.0, github.com/PX4/PX4-Autopilot | BSD-3-Clause | [`PX4-Autopilot.LICENSE`](licenses/PX4-Autopilot.LICENSE) |
| PX4 GPS drivers | submodule of PX4 v1.17.0 | BSD-3-Clause | [`PX4-GPSDrivers.LICENSE`](licenses/PX4-GPSDrivers.LICENSE) |
| NuttX RTOS | PX4 fork, commit fb2fadf6 | Apache-2.0 (+ third-party notices in the file) | [`NuttX.LICENSE`](licenses/NuttX.LICENSE), [`NuttX.NOTICE`](licenses/NuttX.NOTICE) |
| NuttX apps | PX4 fork, commit e37940d | Apache-2.0 | [`NuttX-apps.LICENSE`](licenses/NuttX-apps.LICENSE), [`NuttX-apps.NOTICE`](licenses/NuttX-apps.NOTICE) |
| MAVLink (generated headers) | submodule of PX4 v1.17.0 | MIT (generator output exception) | [`MAVLink.COPYING`](licenses/MAVLink.COPYING) |
| libevents | submodule of PX4 v1.17.0 | BSD-3-Clause | [`libevents.LICENSE`](licenses/libevents.LICENSE) |
| heatshrink | submodule of PX4 v1.17.0 | ISC | [`heatshrink.LICENSE`](licenses/heatshrink.LICENSE) |
| Micro XRCE-DDS Client | submodule of PX4 v1.17.0 | Apache-2.0 | [`Micro-XRCE-DDS-Client.LICENSE`](licenses/Micro-XRCE-DDS-Client.LICENSE) |
| Micro-CDR | dependency of the XRCE-DDS client | Apache-2.0 | [`Micro-CDR.LICENSE`](licenses/Micro-CDR.LICENSE) |

The only change against the upstream sources is the board variant [`../board/peregrine.px4board`](../board/peregrine.px4board), which enables PX4's own `msp_osd` driver. The complete corresponding source is the PX4-Autopilot v1.17.0 tag with its submodules plus that file.

THE FIRMWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND; see the individual licence texts.
