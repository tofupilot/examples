import openhtf as htf
from openhtf.plugs import plug
from multimeter_plug import MultimeterPlug


@plug(multimeter=MultimeterPlug)
@htf.measures(htf.Measurement("voltage").in_range(3.0, 3.5).with_units("V"))
def test_voltage(test, multimeter):
    voltage = multimeter.measure_voltage()
    test.measurements.voltage = voltage


def main():
    test = htf.Test(test_voltage)
    test.execute(lambda: "PCB0001") # UUT S/N


if __name__ == "__main__":
    main()
