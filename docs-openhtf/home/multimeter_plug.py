from openhtf.plugs import BasePlug


class MultimeterPlug(BasePlug):
    # Simulate connecting to the multimeter
    def __init__(self):
        self.connected = True

    # Simulate measuring the voltage
    def measure_voltage(self):
        return 3.3

    # Simulate disconnecting from the multimeter
    # This method is called automatically by OpenHTF at the end of the test
    def tearDown(self):
        self.connected = False
