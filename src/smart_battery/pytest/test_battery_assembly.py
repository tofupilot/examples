from tofupilot import conf, numeric_step, string_step
from datetime import datetime, timedelta
import random
import pytest

# Generate unique serial numbers
part_number_assembly = "SI02430"
revision_assembly = "B"
static_segment = "4J"
batch_number_assembly = "1024"
random_digits_assembly = "".join([str(random.randint(0, 9)) for _ in range(5)])
serial_number_assembly = (
    f"{part_number_assembly}{revision_assembly}{static_segment}{random_digits_assembly}"
)
# To be imporved - for the moment creates a link with sub-units of a fixed serial number
sub_units = [
    {"serial_number": "00786C4J26221"},
    {"serial_number": "00143B4J73889"},
]

# Configure Run information to be sent to TofuPilot
conf.set(
    procedure_id="FVT1",
    serial_number=serial_number_assembly,
    part_number=part_number_assembly,
    batch_number=batch_number_assembly,
    sub_units=sub_units,
)


# Simulate passing probability for a test result
def simulate_test_result(passed_prob):
    return random.random() < passed_prob


# Tests for pytest
def test_battery_connection(step):
    passed = simulate_test_result(0.99)
    assert passed


@pytest.fixture(scope="module")
def voltage_value():
    passed = simulate_test_result(0.98)
    measured_voltage = (
        round(random.uniform(10, 12), 1)
        if passed
        else round(random.uniform(8.0, 9.5), 2)
    )
    return measured_voltage


@numeric_step
def test_voltage_value(step, voltage_value):
    # Test for voltage value using a fixture.
    step.set_units("V").set_limits(low=10.0, high=12.0)
    step.measure(voltage_value)
    assert step()


@pytest.fixture(scope="module")
def internal_resistance():
    passed = simulate_test_result(0.98)
    measured_ir = (
        round(random.uniform(10, 12), 1) if passed else round(random.uniform(15, 20), 1)
    )
    return measured_ir


@numeric_step
def test_internal_resistance(step, internal_resistance):
    step.set_units("mΩ").set_limits(low=5, high=15)
    step.measure(internal_resistance)
    assert step()


@numeric_step
def test_thermal_runaway_detection(step):
    step.set_units("°C").set_limits(low=55, high=65)
    passed = simulate_test_result(0.98)
    value_measured = (
        round(random.uniform(55, 65), 2) if passed else round(random.uniform(66, 70), 2)
    )
    step.measure(value_measured)
    assert step()


@numeric_step
def test_state_of_health(step):
    step.set_units("%").set_limits(low=95)
    passed = simulate_test_result(0.98)
    value_measured = (
        round(random.uniform(95, 100), 1)
        if passed
        else round(random.uniform(85, 94), 1)
    )
    step.measure(value_measured)
    assert step()


@numeric_step
def test_state_of_charge(step, voltage_value, internal_resistance):
    step.set_units("%").set_limits(low=40, high=60)
    passed = simulate_test_result(0.99)
    value_measured = (
        round(random.uniform(40, 60), 1) if passed else round(random.uniform(25, 35), 1)
    )
    step.measure(value_measured)
    assert step()
    # Create report if last step is passed
    report_variables = {
        "report_date": str(datetime.now().strftime("%d.%m.%Y")),
        "serial_number": serial_number_assembly,
        "batch_number": batch_number_assembly,
        "voltage_test_result": str(voltage_value),
        "safety_test_result": "Passed all safety tests",
        "internal_resistance": str(internal_resistance),
    }
    conf.set(report_variables=report_variables)
    assert True
