"""Programmable AC source driving the mains side of the regulation sweep."""

# VISA resource of the AC source on the bench LAN.
AC_SOURCE_RESOURCE = "TCPIP0::192.0.2.11::inst0::INSTR"

LINE_FREQUENCY_HZ = 50.0


class ACSource:
    def __init__(self):
        self._source = None

        # import pyvisa
        #
        # self._source = pyvisa.ResourceManager().open_resource(AC_SOURCE_RESOURCE)
        # self._source.timeout = 10_000
        # self._source.write(f"SOURce:FREQuency {LINE_FREQUENCY_HZ}")
        # self._source.write("OUTPut:STATe ON")

    def __del__(self):
        # self._source.write("OUTPut:STATe OFF")
        pass

    def identity(self) -> str:
        # return self._source.query("*IDN?").strip()
        return "GW-INSTEK,APS-7100,SIMULATED,1.0"

    def set_voltage(self, volts: float) -> None:
        # self._source.write(f"SOURce:VOLTage {volts}")
        # self._source.query("*OPC?")
        pass
