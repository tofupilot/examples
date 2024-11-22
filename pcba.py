import time
from typing import Optional

import openhtf as htf
from openhtf import measures
from openhtf.plugs import plug, user_input
from openhtf.util import units
from openhtf.util.configuration import CONF
from tofupilot.openhtf import TofuPilot

from plug.custom.mock_drone_com import MockDroneCom
from plug.power.mock_psu_control import MockPsuControl
from plug.programmer.dfu_util import DfuUtil
from plug.system.lsusb import Lsusb
from plug.usb_switch.acroname2x4 import Acroname2x4

# Motherboard flash configuration
CONF.declare('firmware_path', default_value='mock_firmware.hex', description='Path to firmware file.')
CONF.declare('mcu', default_value='atmega328p', description='Microcontroller type for avrdude.')
CONF.declare('port', default_value='/dev/ttyUSB0', description='Port for avrdude to use.')

# Motherboard DFU mode VID / PID
CONF.declare('mb_usb_id', default_value='8087:0032', description='Motherboard dfu USB ID')

# Test station specific configuration
CONF.declare('switch_port_nr', default_value=1, description='USB switch port number where the DUT is connected.')

# Simulated run with no hardware or real run?
CONF.declare('simulated', default_value=True, description='Simulated mode toggle.')


## Step 1: check if the motherboard is connected in DFU mode
@plug(lsusb=Lsusb, usb_switch=Acroname2x4, power_supply=MockPsuControl)
@htf.PhaseOptions(repeat_limit=5, timeout_s=10)
def check_mb_alive(lsusb: Lsusb, usb_switch: Acroname2x4, power_supply: MockPsuControl) -> Optional[htf.PhaseResult]:
    usb_switch.enable_port(port_number=CONF.switch_port_nr)  # Turn on USB first
    power_supply.turn_on()  # Then turn power on to enter DFU mode

    if CONF.mb_usb_id in lsusb.list_devices():
        return htf.PhaseResult.CONTINUE
    else:
        time.sleep(1)
        return htf.PhaseResult.REPEAT


@plug(programmer=DfuUtil)
@measures(htf.Measurement('firmware_flashed').equals(True))
## Step 2: program main microcontroller
def flash_motherboard(test: htf.TestApi, programmer: DfuUtil) -> None:
    test.measurements.firmware_flashed = programmer.flash_firmware(
        firmware_path=CONF.firmware_path, vid_pid=CONF.mb_usb_id)


## Step 3: check drone communication
@plug(drone_com=MockDroneCom)
@measures(htf.Measurement('drone_id_after_flash').equals("default-id-123"))
def get_drone_id(test: htf.TestApi, drone_com: MockDroneCom) -> None:
    test.measurements.drone_id_after_flash = drone_com.get_drone_id()


## Step 4: send drone ID (serial number)
@plug(drone_com=MockDroneCom)
@measures(htf.Measurement('drone_production_id'))
def set_drone_id(test: htf.TestApi, drone_com: MockDroneCom) -> None:
    drone_id: str = drone_com.set_drone_id(test.test_record.dut_id)
    test.measurements.drone_production_id = drone_id


## Step 5: check pressure sensor
@plug(drone_com=MockDroneCom)
@htf.measures(
    htf.Measurement("pressure")
    .in_range(900, 1040)  # Reasonnable pressure range at ground level
    .with_units(units.HECTOPASCAL)
    .with_precision(1)  # Rounds to 1 decimal place
)
def check_pressure_sensor(test: htf.TestApi, drone_com: MockDroneCom) -> None:
    test.measurements.pressure = drone_com.get_pressure()


## Teardown
@plug(usb_switch=Acroname2x4, power_supply=MockPsuControl)
def teardown(usb_switch: Acroname2x4, power_supply: MockPsuControl) -> None:
    usb_switch.disable_port(port_number=CONF.switch_port_nr)
    power_supply.turn_off()


# Main test procedure with TofuPilot integration
def main() -> None:
    test = htf.Test(
        check_mb_alive,
        flash_motherboard,
        get_drone_id,
        set_drone_id,
        check_pressure_sensor,
        teardown,
        procedure_name="Test motherboard",
        procedure_id="MBT-1"
    )

    with TofuPilot(test):
        test.execute(test_start=user_input.prompt_for_test_start())


if __name__ == "__main__":
    main()
