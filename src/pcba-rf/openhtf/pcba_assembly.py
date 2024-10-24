import openhtf as htf
from openhtf.util import units
import random
from pathlib import Path
from tofupilot.openhtf import TofuPilot


# Simulate test results with a given pass probability (FPY)
def simulate_test_result(passed_prob):
    return random.random() < passed_prob


# Operator perfom visual inspection
def visual_inspection():
    if simulate_test_result(0.98):
        return htf.PhaseResult.CONTINUE
    else:
        return htf.PhaseResult.STOP


# Validate the backplane interface connectivity
@htf.measures(htf.Measurement("interface").equals(True))
def backplane_interface_validation(test):
    test.measurements.interface = simulate_test_result(0.95)


@htf.measures(htf.Measurement("firmware_version").equals("1.4.3"))
def pcba_firmware_version(test):
    test.measurements.firmware_version = (
        "1.4.3" if simulate_test_result(0.99) else "1.4.2"
    )


# Measure the power consumption of the UUT (in Watts)
@htf.measures(
    htf.Measurement("power_consumption").in_range(maximum=80.0).with_units(units.WATT)
)
def check_power_consumption(test):
    passed = simulate_test_result(1)
    value_measured = (
        round(random.uniform(75, 80), 1) if passed else round(random.uniform(81, 85), 1)
    )
    test.measurements.power_consumption = value_measured


@htf.measures(
    htf.Measurement("thermal_value")
    .in_range(minimum=35.0, maximum=55.0)
    .with_units(units.DEGREE_CELSIUS)
)
def check_thermal_sensor(test):
    passed = simulate_test_result(0.80)
    value_measured = (
        round(random.uniform(35, 55), 1) if passed else round(random.uniform(56, 85), 1)
    )
    test.measurements.thermal_value = value_measured


@htf.measures(
    htf.Measurement("voltage_12V")
    .in_range(minimum=11.5, maximum=12.5)
    .with_units(units.VOLT)
)
def check_power_supply_12V(test):
    passed = simulate_test_result(1)
    value_measured = (
        round(random.uniform(12, 12.5), 1)
        if passed
        else round(random.uniform(10.5, 11.4), 1)
    )
    test.measurements.voltage_12V = value_measured


@htf.measures(
    htf.Measurement("voltage_3V3")
    .in_range(minimum=3.0, maximum=3.6)
    .with_units(units.VOLT)
)
def check_power_supply_3V3(test):
    passed = simulate_test_result(1)
    value_measured = (
        round(random.uniform(3.3, 3.6), 2)
        if passed
        else round(random.uniform(1.1, 2.9), 2)
    )
    test.measurements.voltage_3V3 = value_measured


# Verify read/write eeprom in following functions
@htf.measures(htf.Measurement("eeprom_reading_status").equals(True))
def read_eeprom(test):
    test.measurements.eeprom_reading_status = simulate_test_result(1)


@htf.measures(htf.Measurement("eeprom_writing_status").equals(True))
def write_eeprom(test):
    test.measurements.eeprom_writing_status = simulate_test_result(1)


@htf.measures(htf.Measurement("emmc_status").equals(True))
def read_and_write_eMMC(test):
    test.measurements.emmc_status = simulate_test_result(0.98)


@htf.measures(htf.Measurement("jtag_connector_status").equals(True))
def check_JTAG_connector(test):
    test.measurements.jtag_connector_status = simulate_test_result(1)


@htf.measures(
    htf.Measurement("gain_bandwidth_15GHz")
    .in_range(minimum=-7.2, maximum=-6.8)
    .with_units(units.DECIBEL_MILLIWATTS)
)
def check_gain_bandwidth_at_15GHz(test):
    passed = simulate_test_result(1)
    value_measured = (
        round(random.uniform(-7.2, -6.8), 1)
        if passed
        else round(random.uniform(-7.8, -7.3), 1)
    )
    test.measurements.gain_bandwidth_15GHz = value_measured


@htf.measures(
    htf.Measurement("gain_bandwidth_15p5GHz")
    .in_range(minimum=-7.2, maximum=-6.8)
    .with_units(units.DECIBEL_MILLIWATTS)
)
def check_gain_bandwidth_at_15p5GHz(test):
    passed = simulate_test_result(0.99)
    value_measured = (
        round(random.uniform(-7.2, -6.8), 1)
        if passed
        else round(random.uniform(-7.8, -7.3), 1)
    )
    test.measurements.gain_bandwidth_15p5GHz = value_measured


@htf.measures(
    htf.Measurement("gain_bandwidth_16GHz")
    .in_range(minimum=-7.2, maximum=-6.8)
    .with_units(units.DECIBEL_MILLIWATTS)
)
def check_gain_bandwidth_at_16GHz(test):
    passed = simulate_test_result(1)
    value_measured = (
        round(random.uniform(-7.2, -6.8), 1)
        if passed
        else round(random.uniform(-7.8, -7.3), 1)
    )
    test.measurements.gain_bandwidth_16GHz = value_measured


def load_subunits_serial_numbers(filepath):
    with open(filepath, "r") as f:
        return [line.strip() for line in f]


def main(test_qty):
    filepath = Path("src/pcba-rf/serial_numbers.txt")
    subunits_serial_numbers = load_subunits_serial_numbers(filepath)

    for i in range(test_qty):
        test = htf.Test(
            visual_inspection,
            backplane_interface_validation,
            pcba_firmware_version,
            check_power_supply_12V,
            check_power_supply_3V3,
            check_power_consumption,
            check_thermal_sensor,
            read_eeprom,
            write_eeprom,
            read_and_write_eMMC,
            check_JTAG_connector,
            check_gain_bandwidth_at_15GHz,
            check_gain_bandwidth_at_15p5GHz,
            check_gain_bandwidth_at_16GHz,
            procedure_id="FVT19",
            part_number="00389",
            sub_units=[{"serial_number": subunits_serial_numbers[i]}],
            revision="A",
        )

        # Generate random Serial Number
        random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
        serial_number = f"00389B4J{random_digits}"

        # Execute the test
        with TofuPilot(test):
            test.execute(lambda: serial_number)

    with open(filepath, "w") as f:
        pass  # Empty file after use


if __name__ == "__main__":
    main(10)
