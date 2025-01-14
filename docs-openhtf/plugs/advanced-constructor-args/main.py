import openhtf as htf
from openhtf.plugs import plug
from openhtf.util.configuration import CONF, bind_init_args
from multimeter_plug import MultimeterPlug

COM_PORT_1 = CONF.declare("com_port_1", default_value="COM1")
COM_PORT_2 = CONF.declare("com_port_2", default_value="COM2")


MultimeterPlug1 = bind_init_args(MultimeterPlug, COM_PORT_1)
MultimeterPlug2 = bind_init_args(MultimeterPlug, COM_PORT_2)


@plug(multimeter=MultimeterPlug1)
def test_voltage_1(test, multimeter):
    multimeter.measure_voltage()


@plug(multimeter=MultimeterPlug2)
def test_voltage_2(test, multimeter):
    multimeter.measure_voltage()


def main():
    test = htf.Test(test_voltage_1, test_voltage_2)
    test.execute(lambda: "PCB0001")  # UUT S/N


if __name__ == "__main__":
    main()
