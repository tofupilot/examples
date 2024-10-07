from tofupilot import conf, numeric_step
import random
import pytest

# Generate unique serial numbers
part_number_cell = "00143"
revision_cell = "B"
static_segment = "4J"
batch_number_cell = "1024"
random_digits_cell = "".join([str(random.randint(0, 9)) for _ in range(5)])
serial_number_cell = (
    f"{part_number_cell}{revision_cell}{static_segment}{random_digits_cell}"
)

# Configure Run information to be sent to TofuPilot
conf.set(
    procedure_id="FVT2",
    serial_number=serial_number_cell,
    part_number=part_number_cell,
    batch_number=batch_number_cell,
)


# Simulate passing probability for a test result
def simulate_test_result(passed_prob):
    return random.random() < passed_prob


# Tests for pytest
@numeric_step
def test_esr(step):
    step.set_units("mΩ").set_limits(low=5, high=15)
    value_measured = 14.33
    step.measure(value_measured)
    assert step()


@numeric_step
def test_cell_voltage(step):
    step.set_units("V").set_limits(low=3, high=3.5)
    passed = simulate_test_result(0.98)
    value_measured = (
        round(random.uniform(3.0, 3.5), 2)
        if passed
        else round(random.uniform(2.5, 2.9), 2)
    )
    step.measure(value_measured)
    assert step()


@numeric_step
def test_ir(step):
    step.set_units("mΩ").set_limits(low=5, high=15)
    passed = simulate_test_result(0.98)
    value_measured = (
        round(random.uniform(5, 10), 2) if passed else round(random.uniform(15, 20), 2)
    )
    step.measure(value_measured)
    assert step()


@numeric_step
def test_charge_discharge_cycle(step):
    step.set_units("% Capacity").set_limits(low=95, high=100)
    passed = simulate_test_result(0.98)
    value_measured = (
        round(random.uniform(95, 100), 1)
        if passed
        else round(random.uniform(80, 94), 1)
    )
    step.measure(value_measured)
    assert step()
