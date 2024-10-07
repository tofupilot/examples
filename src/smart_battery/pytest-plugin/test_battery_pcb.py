from tofupilot import conf, numeric_step, string_step
import random
import os
import pytest

# Generate unique serial numbers
part_number_pcb = "00786"
revision_pcb = "A"
static_segment = "4J"
batch_number_pcb = "1024"
random_digits_pcb = "".join([str(random.randint(0, 9)) for _ in range(5)])
serial_number_pcb = (
    f"{part_number_pcb}{revision_pcb}{static_segment}{random_digits_pcb}"
)

# Configure Run information to be sent to TofuPilot
conf.set(
    procedure_id="FVT1",
    serial_number=serial_number_pcb,
    part_number=part_number_pcb,
    batch_number=batch_number_pcb,
)


# Simulate passing probability for a test result
def simulate_test_result(passed_prob):
    return random.random() < passed_prob


# Tests for pytest
@string_step
def test_flash_firmware_and_version(step):
    step.set_limit("v2.5.1")
    passed = simulate_test_result(0.99)
    assert passed
    value_measured = "v2.5.1"
    step.measure(value_measured)
    assert step()


def test_configuration_battery_gauge():
    passed = simulate_test_result(0.98)
    assert passed


def test_get_calibration_values_and_internal_status(step):
    passed = simulate_test_result(0.99)
    assert passed


@numeric_step
def test_overvoltage_protection(step):
    step.set_units("V").set_limits(low=4.20, high=4.25)
    passed = simulate_test_result(0.98)
    value_measured = (
        round(random.uniform(4.2, 4.25), 2)
        if passed
        else round(random.uniform(4.25, 5.6), 2)
    )
    step.measure(value_measured)
    assert step()


@numeric_step
def test_undervoltage_protection(step):
    step.set_units("V").set_limits(low=2.5, high=2.6)
    passed = simulate_test_result(0.98)
    value_measured = (
        round(random.uniform(2.5, 2.6), 2)
        if passed
        else round(random.uniform(2.3, 2.4), 2)
    )
    step.measure(value_measured)
    assert step()


def test_LED_and_button(step):
    passed = simulate_test_result(0.95)
    assert passed


def test_save_information_in_memory(step):
    passed = simulate_test_result(0.99)
    assert passed


def test_config_battery_gauge(step):
    passed = simulate_test_result(0.99)
    assert passed


@numeric_step
def test_calibrate_temperature(step):
    step.set_name("calibrate_temperature").set_units("°C").set_limits(low=20, high=25)
    passed = simulate_test_result(0.99)
    value_measured = (
        round(random.uniform(20.0, 25.0), 1)
        if passed
        else round(random.uniform(15.0, 20.0), 1)
    )
    step.measure(value_measured)
    assert step()


def test_visual_inspection():
    attachment = ["./pcb_coating.jpeg"]
    assert attachment is not None
    conf.set(attachments=attachment)
