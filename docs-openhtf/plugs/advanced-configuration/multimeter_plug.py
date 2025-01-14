from openhtf import BasePlug
from openhtf.util import configuration

# Define `firmware_path` configuration
configuration.CONF.declare(
    "com_port",
    default_value="COM1",
    description="COM port to connect to the multimeter",
)


class MultimeterPlug(BasePlug):
    # Simulate connecting to the multimeter
    def __init__(self):
        self.com_port = configuration.CONF.load("com_port")
        self.connected = True

    # Simulate measuring the voltage
    def measure_voltage(self):
        return 3.3

    # Simulate disconnecting from the multimeter
    # This method is called automatically by OpenHTF at the end of the test
    def tearDown(self):
        self.connected = False
