"""Inline load cell reading the force at which the dome switch actuates."""

# Load cell indicator on the bench LAN.
import random

GAUGE_RESOURCE = "TCPIP0::192.0.2.21::inst0::INSTR"

# Ramp until the switch reports, or give up.
RAMP_LIMIT_G = 120.0


class ForceGauge:
    def __init__(self):
        self._gauge = None

        # import pyvisa
        #
        # self._gauge = pyvisa.ResourceManager().open_resource(GAUGE_RESOURCE)
        # self._gauge.timeout = 10_000
        # self._gauge.write("UNIT:FORCe GRAM")

    def __del__(self):
        pass

    def identity(self) -> str:
        # return self._gauge.query("*IDN?").strip()
        return "SIMULATED-LOAD-CELL,1.0"

    def zero(self) -> None:
        # self._gauge.write("SENSe:CORRection:COLLect:ZERO")
        # self._gauge.query("*OPC?")
        pass

    def ramp_until_actuation(self) -> float:
        """Ramp force at the pad centre; return the force at the click, in grams."""
        # The switch closure is what stops the ramp, so the gauge is read on
        # the edge rather than sampled and compared afterwards.
        # self._gauge.write(f"SOURce:FORCe:RAMP {RAMP_LIMIT_G}")
        # self._gauge.write("TRIGger:SOURce EXTernal")
        # return float(self._gauge.query("FETCh:FORCe?"))

        return round(random.gauss(60.5, 3.4), 1)
