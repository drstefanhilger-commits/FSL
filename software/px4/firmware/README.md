# Prebuilt firmware

`holybro_kakuteh7_peregrine.px4` = PX4 **v1.17.0** (tag), target `holybro_kakuteh7` + [`../board/peregrine.px4board`](../board/peregrine.px4board) (adds the `msp_osd` HDZero OSD driver). Built with `make holybro_kakuteh7_peregrine`, arm-none-eabi-gcc 13.2.rel1. Flash use 96.6 %.

SHA-256: `a9acbd8e389d4e1ff004f46fa3627c496030bca34c84e2b4663825f9c47f0a0b`

Flash with QGroundControl: *Vehicle Setup → Firmware → PX4 Pro → Advanced → Custom firmware file*. The PX4 bootloader must be on the board first (see `../../SETUP.md` §1). Not flight-tested.
