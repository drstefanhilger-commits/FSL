# Wiring

Every cable in the CAD assembly is modelled end to end, from a real pad or connector to a real pad or connector. The harness parts are colour-coded in the model and in the renders:

| # | Link | Colour in CAD | From → To | Connector / pads | Route |
|---|------|---------------|-----------|------------------|-------|
| 1 | FC ↔ ESC | (inside the stack) | Kakute H7 ↔ Tekko32 4-in-1 | 8-pin JST-SH, supplied with the stack | Straight down between the stacked boards (30.5 mm pattern). It carries motor signals, current sense and ESC telemetry (UART7; PX4 starts the DShot telemetry there automatically). |
| 2 | Motor leads ×4 | Orange | ESC motor pads → motors | 3 × 18 AWG per motor, soldered | The front and rear pad rows each feed two motors. The leads bundle beside the stack, rise into the root fairing, run through the **6 × 6 mm groove on the split face of `Wing - Bottom Part`**, then up the nacelle slot to the motor base. |
| 3 | Battery lead | Red | ESC battery pads → XT60 | 12 AWG pigtail + XT60 pair | Short riser from the pads to an XT60 lying across the tray. The battery's own XT60 plugs in from the rear. Solder the low-ESR capacitor across the battery pads. |
| 4 | VTX power + UART | Yellow | FC HD/VTX port → HDZero VTX | 6-pin JST-SH both ends (9 V, GND, UART1 TX/RX) | Runs along the tray to the VTX at the front of the bay. UART1 is PX4's `TELEM1`: `MSP_OSD_CONFIG = 101` (MSP DisplayPort OSD), `MAV_0_CONFIG = 0`. |
| 5 | Video antenna coax | Black | VTX U.FL → tail antenna | U.FL, 1.13 mm coax (300 mm extension) | Runs aft under the tray to the tail and leaves on the body axis through the Ø3.6 mm hole (Ø5.8 × 2 mm counterbore for the ferrule). |
| 6 | Camera MIPI | Blue | VTX MIPI port → HDZero Micro V3 (V2 in the CAD, same mount) | HDZero MIPI ribbon, 250 mm | About 152 mm of route plus slack, forward into the nose cradle. Keep it away from the motor leads. |
| 7 | GPS | Cyan | Micro M10 (nose) → FC pads | JST-GH 6-pin at the GPS, soldered at the FC: 5 V, GND, GPS TX → **R4**, GPS RX → **T4**, SCL, SDA | The GPS sits in the nose cone above the camera, screwed through the bulkhead. The cable runs aft along the canopy side. UART4 is PX4's `GPS1` (`GPS_1_CONFIG = 201`), the compass is on the external I²C bus (`SYS_HAS_MAG = 1`). **Not UART3:** PX4 uses UART3 as its system console. |
| 8 | ELRS receiver | Green | RX (beside the battery, −X side) → FC UART6 pads | 4 × 28 AWG: 5 V, GND, RX-TX → **R6**, RX-RX → **T6** | Short run forward to the stack. The 2.4 GHz T-antenna lies along the body axis on the bottom skin, away from the video antenna. UART6 is PX4's RC port: `RC_INPUT_PROTO = 6` (CRSF, telemetry included). |
| 9 | Airspeed sensor | (not in CAD yet) | Matek ASPD-4525 → FC I²C pads | JST-GH 4-pin: 5 V, GND, SCL, SDA (shared with the GPS compass bus) | Mount the board inside the nose bay. Run the silicone tubes to a pitot tube that pokes forward through a canard leading edge or the nose-to-body joint, **out of the prop wash and at least 20 mm ahead of the local surface**. `SENS_EN_MS4525DO = 1`. |

## Notes

- **Wing split.** Each wing is printed as a top part (leading-edge beam + motor mount) and a bottom part (panel). Lay the motor leads in the bottom part's groove, then close the wing on 4 filament pins (Ø1.75 mm) with CA or epoxy. The leads never have to be pulled through a closed tube.
- **Motor direction.** Reverse a motor with the DShot *Set Spin Direction* buttons in QGC → Actuators (PX4 has no BLHeli/AM32 passthrough), or swap any two motor wires. The motor order is PX4 Quad X in the hover attitude, the same numbering as ArduPilot (see [`software/SETUP.md`](../software/SETUP.md)).
- **RF separation.** The 5.8 GHz video antenna exits the tail and the 2.4 GHz RX antenna lies on the bottom skin, so neither antenna shadows the other in hover (nose up) or in forward flight.
- **Coming from ArduPilot?** Only one wire changes: the GPS UART moves from T3/R3 to **T4/R4**. See [`software/px4/MIGRATION.md`](../software/px4/MIGRATION.md).
- **Checks before the first power-up.** Beep out the battery pads for shorts, check the XT60 polarity, and power the stack from a smoke stopper the first time.
