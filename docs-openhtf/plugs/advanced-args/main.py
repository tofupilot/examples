import openhtf as htf
from openhtf.plugs import plug
from openhtf.util.configuration import CONF, bind_init_args
from multimeter_plug import MultimeterPlug

COM_PORT_1 = CONF.declare("com_port_1", default_value="COM1")
COM_PORT_2 = CONF.declare("com_port_2", default_value="COM2")


MultimeterPlug1 = bind_init_args(MultimeterPlug, COM_PORT_1)
MultimeterPlug2 = bind_init_args(MultimeterPlug, COM_PORT_2)


@plug(multimeter=MultimeterPlug1)
@htf.measures(htf.Measurement("voltage").in_range(3.0, 3.5).with_units("V"))
def test_voltage(test, multimeter):
    voltage = multimeter.measure_voltage()
    test.measurements.voltage = voltage


@plug(multimeter=MultimeterPlug2)
@htf.measures(htf.Measurement("voltage").in_range(3.0, 3.5).with_units("V"))
def test_voltage(test, multimeter):
    voltage = multimeter.measure_voltage()
    test.measurements.voltage = voltage


def main():
    test = htf.Test(test_voltage)
    test.execute(lambda: "PCB0001")  # UUT S/N


if __name__ == "__main__":
    main()
