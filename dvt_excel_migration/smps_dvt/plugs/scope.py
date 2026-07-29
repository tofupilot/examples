"""Tektronix MSO5-series oscilloscope.

Reads the same figures a hand-written report transcribes off the screen
(Peak-to-Peak and RMS) and, unlike a screenshot, also returns the waveform
behind them.

The methods below generate representative data so the procedure runs anywhere.
Each keeps its real instrument call directly above, commented out: swap the two
and the same procedure drives the bench.
"""

import math
import random

# VISA resource of the scope on the bench LAN.
SCOPE_RESOURCE = "TCPIP0::192.0.2.10::inst0::INSTR"

RAIL_23V_NOM = 23.0
RAIL_9V_NOM = 9.0
CH_23V = 1

# Rectified mains ripple sits at twice the line frequency.
LINE_FREQUENCY_HZ = 50.0


class Oscilloscope:
    def __init__(self):
        self._scope = None

        # import pyvisa
        #
        # self._scope = pyvisa.ResourceManager().open_resource(SCOPE_RESOURCE)
        # self._scope.timeout = 20_000
        # self._scope.write("*RST")
        # # 12-bit High Res: at 400 mV of ripple on a 23 V rail the extra bits
        # # are the difference between measuring ripple and measuring the
        # # quantiser.
        # self._scope.write("ACQuire:MODe HIRes")
        # self._scope.write("HORizontal:MODe AUTO")

    def identity(self) -> str:
        """Model and firmware, recorded with the run for traceability."""
        # return self._scope.query("*IDN?").strip()
        return "TEKTRONIX,MSO54,SIMULATED,1.0"

    def configure_channel(self, channel: int, volts_per_div: float) -> None:
        """AC-couple the rail so its DC level does not eat the vertical range."""
        # self._scope.write(f"DISplay:GLObal:CH{channel}:STATE ON")
        # self._scope.write(f"CH{channel}:COUPling AC")
        # # 20 MHz is the usual bandwidth limit for a ripple measurement.
        # self._scope.write(f"CH{channel}:BANdwidth 20E6")
        # self._scope.write(f"CH{channel}:SCAle {volts_per_div}")
        # self._scope.write(f"CH{channel}:OFFSet 0")
        pass

    def set_timebase(self, seconds_per_div: float) -> None:
        # self._scope.write(f"HORizontal:SCAle {seconds_per_div}")
        pass

    def acquire(self) -> None:
        """One single-sequence acquisition, so every read is the same capture."""
        # self._scope.write("ACQuire:STOPAfter SEQuence")
        # self._scope.write("ACQuire:STATE RUN")
        # self._scope.query("*OPC?")
        pass

    def measure_dc(self, channel: int) -> float:
        """Rail voltage in volts, DC-coupled mean."""
        # self._scope.write(f"CH{channel}:COUPling DC")
        # self.acquire()
        # self._scope.write("MEASUrement:ADDMEAS MEAN")
        # self._scope.write(f"MEASUrement:MEAS1:SOUrce CH{channel}")
        # self._scope.write("MEASUrement:MEAS1:TYPe MEAN")
        # self._scope.query("*OPC?")
        # return float(
        #     self._scope.query("MEASUrement:MEAS1:RESUlt:CURRentacq:MEAN?")
        # )
        nominal = RAIL_23V_NOM if channel == CH_23V else RAIL_9V_NOM
        return round(random.gauss(nominal, 0.04), 3)

    def measure_ripple(self, channel: int):
        """Peak-to-peak and RMS ripple in millivolts, AC-coupled."""
        # self._scope.write("MEASUrement:ADDMEAS PK2PK")
        # self._scope.write(f"MEASUrement:MEAS1:SOUrce CH{channel}")
        # self._scope.write("MEASUrement:MEAS1:TYPe PK2PK")
        # self._scope.write("MEASUrement:ADDMEAS RMS")
        # self._scope.write(f"MEASUrement:MEAS2:SOUrce CH{channel}")
        # self._scope.write("MEASUrement:MEAS2:TYPe RMS")
        # self._scope.query("*OPC?")
        # peak_volts = float(
        #     self._scope.query("MEASUrement:MEAS1:RESUlt:CURRentacq:MEAN?")
        # )
        # rms_volts = float(
        #     self._scope.query("MEASUrement:MEAS2:RESUlt:CURRentacq:MEAN?")
        # )
        # return peak_volts * 1000.0, rms_volts * 1000.0
        peak_mv = random.uniform(120.0, 340.0)
        # Rectified-mains ripple sits near a crest factor of 4.
        return round(peak_mv, 1), round(peak_mv / 4.2, 2)

    def capture_waveform(self, channel: int):
        """The trace behind those numbers, as (seconds, millivolts).

        The record is decimated to a couple of thousand points: enough to keep
        the ripple envelope, small enough to store on every run.
        """
        # self._scope.write(f"DATa:SOUrce CH{channel}")
        # self._scope.write("DATa:ENCdg ASCII")
        # self._scope.write("DATa:STARt 1")
        # record = int(self._scope.query("HORizontal:RECOrdlength?"))
        # self._scope.write(f"DATa:STOP {record}")
        #
        # counts = [float(v) for v in self._scope.query("CURVe?").split(",")]
        # y_multiplier = float(self._scope.query("WFMOutpre:YMUlt?"))
        # y_offset = float(self._scope.query("WFMOutpre:YOFf?"))
        # y_zero = float(self._scope.query("WFMOutpre:YZEro?"))
        # x_increment = float(self._scope.query("WFMOutpre:XINcr?"))
        #
        # stride = max(1, len(counts) // 2000)
        # times, values = [], []
        # for index in range(0, len(counts), stride):
        #     volts = (counts[index] - y_offset) * y_multiplier + y_zero
        #     times.append(index * x_increment)
        #     values.append(volts * 1000.0)
        # return times, values

        points = 500
        duration = 0.2  # 10 ms/div across 20 divisions
        step = duration / points
        amplitude = random.uniform(60.0, 170.0)
        ripple_hz = 2 * LINE_FREQUENCY_HZ

        times, values = [], []
        for index in range(points):
            moment = index * step
            fundamental = amplitude * math.sin(2 * math.pi * ripple_hz * moment)
            # Switching noise rides on the rectified ripple.
            noise = random.gauss(0, amplitude * 0.06)
            times.append(round(moment, 6))
            values.append(round(fundamental + noise, 3))
        return times, values
