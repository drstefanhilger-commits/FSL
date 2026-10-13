#!/usr/bin/env python3
"""Automated VTOL test flight against a running PX4 SITL instance.

Sequence: (optional) load parameters -> arm -> takeoff in hover -> transition to
fixed-wing -> loiter in forward flight -> back-transition -> land -> disarm.
Prints a summary and exits 0 only if every phase completed.

Usage:
  flight_test.py [--url udpin:0.0.0.0:14540] [--alt 30] [--fw-time 40]
                 [--params ../peregrine-kakuteh7.params] [--include-airspeeds]

--params loads only the flight-logic parameters of a QGC .params file
(transitions, differential thrust, FW throttle limits, failsafes). Hardware-
specific ones (outputs, serial ports, sensors, battery, geometry, hover thrust)
are skipped because the simulated airframe is a different vehicle. FW_AIRSPD_*
are skipped too unless --include-airspeeds is given.

Requires: pip install pymavlink
"""
import argparse, math, statistics, sys, time
from pymavlink import mavutil

# parameters that describe the real aircraft's hardware: never pushed into SITL
HW_PREFIXES = ('PWM_', 'DSHOT_', 'MOT_', 'CA_', 'MAV_', 'MSP_', 'OSD_', 'GPS_', 'RC_',
               'SENS_', 'BAT', 'SYS_HAS_', 'ASPD_', 'COM_FLTMODE', 'MPC_THR_HOVER',
               'FW_USE_AIRSPD', 'IMU_', 'EKF2_', 'VT_TYPE')
AIRSPEED_PARAMS = ('FW_AIRSPD_STALL', 'FW_AIRSPD_MIN', 'FW_AIRSPD_TRIM', 'FW_AIRSPD_MAX')

VTOL_STATE = {0: 'UNDEFINED', 1: 'TRANSITION_TO_FW', 2: 'TRANSITION_TO_MC', 3: 'MC', 4: 'FW'}
LANDED = {0: 'UNDEFINED', 1: 'ON_GROUND', 2: 'IN_AIR', 3: 'TAKEOFF', 4: 'LANDING'}


class Flight:
    def __init__(self, url):
        print(f'connecting to {url} ...')
        self.m = mavutil.mavlink_connection(url, source_system=245)
        self.m.wait_heartbeat(timeout=60)
        print(f'heartbeat from system {self.m.target_system}')
        self.vtol_state = 0
        self.landed = 0
        self.alt = float('nan')
        self.airspeed = float('nan')
        self.roll = self.pitch = float('nan')
        self.log = []          # (t, phase, alt, airspeed, roll_deg, pitch_deg, vtol_state)
        self.phase = 'init'
        self.t0 = time.time()
        self.msgs = []

    # ---------- message pump ----------
    def handle(self, msg):
        t = msg.get_type()
        if t == 'EXTENDED_SYS_STATE':
            self.vtol_state, self.landed = msg.vtol_state, msg.landed_state
        elif t == 'GLOBAL_POSITION_INT':
            self.alt = msg.relative_alt / 1000.0
        elif t == 'VFR_HUD':
            self.airspeed = msg.airspeed
        elif t == 'ATTITUDE':
            self.roll, self.pitch = math.degrees(msg.roll), math.degrees(msg.pitch)
            self.log.append((time.time() - self.t0, self.phase, self.alt, self.airspeed,
                             self.roll, self.pitch, self.vtol_state))
        elif t == 'STATUSTEXT':
            self.msgs.append(msg.text)
            print(f'  [PX4] {msg.text}')

    def pump(self, dt=0.05):
        end = time.time() + dt
        while True:
            msg = self.m.recv_match(blocking=True, timeout=max(0.0, end - time.time()))
            if msg is not None:
                self.handle(msg)
            if msg is None or time.time() >= end:
                break

    def recv(self, mtype, timeout, pred=lambda m: True):
        """Wait for a message of type mtype matching pred, handling everything else."""
        end = time.time() + timeout
        while time.time() < end:
            msg = self.m.recv_match(blocking=True, timeout=max(0.0, end - time.time()))
            if msg is None:
                continue
            if msg.get_type() == mtype and pred(msg):
                return msg
            self.handle(msg)
        return None

    def wait(self, cond, timeout, what):
        end = time.time() + timeout
        while time.time() < end:
            self.pump(0.1)
            if cond():
                return True
        print(f'TIMEOUT waiting for {what}')
        return False

    # ---------- commands ----------
    def cmd(self, command, *p, timeout=5):
        p = list(p) + [0] * (7 - len(p))
        for _ in range(3):
            self.m.mav.command_long_send(self.m.target_system, self.m.target_component,
                                         command, 0, *p)
            ack = self.recv('COMMAND_ACK', timeout, lambda m: m.command == command)
            if ack:
                return ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED
        return False

    def set_param(self, name, value, is_int):
        ptype = mavutil.mavlink.MAV_PARAM_TYPE_INT32 if is_int else mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        if is_int:  # PX4 transports INT32 bit-for-bit in the float field
            import struct
            value = struct.unpack('f', struct.pack('i', int(value)))[0]
        for _ in range(3):
            self.m.mav.param_set_send(self.m.target_system, self.m.target_component,
                                      name.encode(), float(value), ptype)
            if self.recv('PARAM_VALUE', 2, lambda m: m.param_id == name):
                return True
        return False

    def stream_rates(self):
        for msg_id, hz in ((mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 20),
                           (mavutil.mavlink.MAVLINK_MSG_ID_EXTENDED_SYS_STATE, 5),
                           (mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD, 5),
                           (mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 10)):
            self.cmd(mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, msg_id, 1e6 / hz, timeout=1)


def load_params(fl, path, include_airspeeds):
    applied, skipped = [], []
    for line in open(path):
        if not line.strip() or line.startswith('#'):
            continue
        _, _, name, value, typ = line.rstrip('\n').split('\t')
        if name.startswith(HW_PREFIXES) or (name in AIRSPEED_PARAMS and not include_airspeeds):
            skipped.append(name)
            continue
        ok = fl.set_param(name, float(value), typ == '6')
        (applied if ok else skipped).append(f'{name}={value}' if ok else name + '(FAILED)')
    print(f'applied {len(applied)} params: {", ".join(applied)}')
    print(f'skipped {len(skipped)} hardware/airframe-specific params')


def phase_stats(log, phase):
    rows = [r for r in log if r[1] == phase]
    if not rows:
        return {}
    alts = [r[2] for r in rows if not math.isnan(r[2])]
    asp = [r[3] for r in rows if not math.isnan(r[3])]
    roll = [r[4] for r in rows]
    pitch = [r[5] for r in rows]
    return {
        'duration_s': round(rows[-1][0] - rows[0][0], 1),
        'alt_min_m': round(min(alts), 1) if alts else None,
        'alt_max_m': round(max(alts), 1) if alts else None,
        'airspeed_mean_ms': round(statistics.mean(asp), 1) if asp else None,
        'airspeed_max_ms': round(max(asp), 1) if asp else None,
        'roll_std_deg': round(statistics.pstdev(roll), 1) if len(roll) > 1 else None,
        'pitch_std_deg': round(statistics.pstdev(pitch), 1) if len(pitch) > 1 else None,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--url', default='udpin:0.0.0.0:14540')
    ap.add_argument('--alt', type=float, default=30.0, help='takeoff altitude [m]')
    ap.add_argument('--fw-time', type=float, default=40.0, help='seconds of forward flight')
    ap.add_argument('--params', help='QGC .params file to apply (flight-logic subset)')
    ap.add_argument('--include-airspeeds', action='store_true')
    a = ap.parse_args()

    fl = Flight(a.url)
    fl.stream_rates()
    if a.params:
        load_params(fl, a.params, a.include_airspeeds)

    results = {}
    C = mavutil.mavlink

    # ---- arm (retry until the estimator is ready) ----
    fl.phase = 'preflight'
    armed = False
    for _ in range(60):
        fl.pump(1.0)
        if fl.cmd(C.MAV_CMD_COMPONENT_ARM_DISARM, 1, timeout=2):
            armed = True
            break
    results['arm'] = armed
    if not armed:
        return finish(fl, results)

    # ---- takeoff (hover) ----
    fl.phase = 'takeoff'
    fl.set_param('MIS_TAKEOFF_ALT', a.alt, False)   # NAV_TAKEOFF param7 would be AMSL
    nan = float('nan')
    fl.cmd(C.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, nan, nan, nan, nan)
    results['takeoff'] = fl.wait(lambda: fl.alt > a.alt - 2, 60, f'altitude {a.alt} m')
    fl.phase = 'hover'
    fl.pump(5)
    if not results['takeoff']:
        return finish(fl, results)

    # ---- front transition ----
    fl.phase = 'transition_fw'
    t = time.time()
    fl.cmd(C.MAV_CMD_DO_VTOL_TRANSITION, C.MAV_VTOL_STATE_FW)
    results['transition_fw'] = fl.wait(lambda: fl.vtol_state == C.MAV_VTOL_STATE_FW, 30, 'FW state')
    results['transition_fw_time_s'] = round(time.time() - t, 1)
    if not results['transition_fw']:
        return finish(fl, results)

    # ---- forward flight (Hold = loiter around the current point) ----
    fl.phase = 'fw'
    fl.cmd(C.MAV_CMD_DO_SET_MODE, C.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 4, 3)  # AUTO.LOITER
    end = time.time() + a.fw_time
    while time.time() < end:
        fl.pump(0.5)
    results['fw_still_fw'] = fl.vtol_state == C.MAV_VTOL_STATE_FW

    # ---- back transition ----
    fl.phase = 'transition_mc'
    t = time.time()
    fl.cmd(C.MAV_CMD_DO_VTOL_TRANSITION, C.MAV_VTOL_STATE_MC)
    results['transition_mc'] = fl.wait(lambda: fl.vtol_state == C.MAV_VTOL_STATE_MC, 30, 'MC state')
    results['transition_mc_time_s'] = round(time.time() - t, 1)
    fl.phase = 'hover2'
    fl.pump(5)

    # ---- land ----
    fl.phase = 'land'
    fl.cmd(C.MAV_CMD_NAV_LAND, 0, 0, 0, float('nan'), float('nan'), float('nan'), 0)
    results['landed'] = fl.wait(lambda: fl.landed == C.MAV_LANDED_STATE_ON_GROUND, 120, 'landing')
    fl.pump(3)
    return finish(fl, results)


def finish(fl, results):
    print('\n===== RESULT =====')
    for k, v in results.items():
        print(f'{k:24s} {v}')
    for ph in ('hover', 'transition_fw', 'fw', 'transition_mc', 'land'):
        s = phase_stats(fl.log, ph)
        if s:
            print(f'{ph:14s} ' + '  '.join(f'{k}={v}' for k, v in s.items()))
    errors = [m for m in fl.msgs if any(w in m.lower() for w in ('fail', 'error', 'abort', 'reject'))]
    if errors:
        print('warnings/errors from PX4:\n  ' + '\n  '.join(errors))
    ok = all(v for k, v in results.items() if isinstance(v, bool))
    print('PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
