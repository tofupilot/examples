"""Cartesian probe pressing a calibrated force at a commanded x/y target.

Two halves on a real bench: the motion controller that puts the tip somewhere,
and the HID read that says where the pad thought it was touched. The positional
error is the distance between the two, so both have to come from the same press.
"""

# Motion controller on the bench LAN.
import random

ROBOT_RESOURCE = "TCPIP0::192.0.2.20::inst0::INSTR"

# Pad geometry, mm. The border strip where the spec relaxes its limit.
PAD_W, PAD_H = 105.0, 65.0
EDGE_BAND = 3.5

# Probe force held constant across the grid so error stays comparable.
PROBE_FORCE_G = 60.0


class TouchRobot:
    def __init__(self):
        self._axes = None
        self._hid = None

        # import pyvisa
        # import hid
        #
        # self._axes = pyvisa.ResourceManager().open_resource(ROBOT_RESOURCE)
        # self._axes.timeout = 10_000
        # self._axes.write("HOME")
        # self._axes.query("*OPC?")
        # self._axes.write(f"FORCe {PROBE_FORCE_G}")
        #
        # # The pad under test, as the OS sees it.
        # self._hid = hid.Device(vid=0x0000, pid=0x0000)

    def __del__(self):
        # self._axes.write("PARK")
        pass

    def identity(self) -> str:
        # return self._axes.query("*IDN?").strip()
        return "SIMULATED-XY-STAGE,1.0"

    def in_edge_band(self, x: float, y: float) -> bool:
        return (
            x < EDGE_BAND
            or y < EDGE_BAND
            or x > PAD_W - EDGE_BAND
            or y > PAD_H - EDGE_BAND
        )

    def press(self, x: float, y: float) -> tuple[float, float]:
        """Press at a commanded target; return the contact the pad reported."""
        # self._axes.write(f"MOVE {x:.3f} {y:.3f}")
        # self._axes.query("*OPC?")
        # self._axes.write("PRESS")
        # self._axes.query("*OPC?")
        #
        # # Digitizer report: absolute X/Y in himetric (0.01 mm), the unit the
        # # Precision Touchpad tests report distances in.
        # report = self._hid.read(64, timeout=1000)
        # reported_x = int.from_bytes(report[2:4], "little") / 100.0
        # reported_y = int.from_bytes(report[4:6], "little") / 100.0
        # return reported_x, reported_y

        # Simulated: the sensor is markedly less linear near the border, which
        # is the whole reason the spec carries two limits.
        sigma = 0.42 if self.in_edge_band(x, y) else 0.14
        return x + random.gauss(0.0, sigma), y + random.gauss(0.0, sigma)
