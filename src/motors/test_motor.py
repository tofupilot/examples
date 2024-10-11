from tofupilot import TofuPilotClient
from datetime import datetime, timedelta
import random
import uuid

client = TofuPilotClient()


# Simulate FPY for each step
def simulate_test_result(passed_prob):
    return random.random() < passed_prob


# Boolean Steps
def visual_inspection_connector():
    passed = simulate_test_result(1)
    return passed, None, None, None, None


def power_on_test():
    passed = simulate_test_result(1)
    return passed, None, None, None, None


def motor_startup_test():
    passed = simulate_test_result(0.99)
    return passed, None, None, None, None


def speed_consistency_no_load_test():
    passed = simulate_test_result(0.98)
    return passed, None, None, None, None


def encoder_feedback_test():
    passed = simulate_test_result(0.99)
    return passed, None, None, None, None


def thermal_stability_test():
    passed = simulate_test_result(0.98)
    return passed, None, None, None, None


# Numeric Measurement Steps
# Verifies that the motor receives the correct voltage and current when powered on.
def power_supply_check_voltage():
    passed = simulate_test_result(0.99)
    value_measured = (
        round(random.uniform(11.5, 12.5), 1)
        if passed
        else round(random.uniform(10.0, 11.0), 1)
    )
    return passed, value_measured, "V", 11.5, 12.5


def power_supply_check_current():
    passed = simulate_test_result(0.99)
    value_measured = (
        round(random.uniform(0, 1.5), 2) if passed else round(random.uniform(1.6, 2), 2)
    )
    return passed, value_measured, "A", None, 1.50


# Evaluates the RPM of the motor without any load to verify speed consistency.
def motor_startup_rpm():
    passed = simulate_test_result(0.99)
    value_measured = (
        round(random.uniform(100, 1500)) if passed else round(random.uniform(50, 99))
    )
    return passed, value_measured, "RPM", 100, None


# Verifies that the encoder is providing accurate feedback for speed and position.
def encoder_feedback_measurement():
    passed = simulate_test_result(0.99)
    value_measured = (
        round(random.uniform(0.5, 4.9), 1)
        if passed
        else round(random.uniform(5.1, 10), 1)
    )
    return passed, value_measured, "% deviation", 0, 5


def backlash_response_time_test():
    passed = simulate_test_result(0.95)
    value_measured = (
        round(random.uniform(0, 0.19), 3)
        if passed
        else round(random.uniform(0.21, 0.5), 3)
    )
    return passed, value_measured, "seconds", None, 0.2


#  Runs the motor at full speed and then tests the braking system
def full_speed_braking_test():
    passed = simulate_test_result(0.8)
    value_measured = (
        round(random.uniform(1.5, 2), 2) if passed else round(random.uniform(2.1, 3), 2)
    )
    return passed, value_measured, "seconds", None, 2


# Monitors the motor’s temperature when running under load.
def thermal_reading():
    passed = simulate_test_result(0.75)
    value_measured = (
        round(random.uniform(75, 80), 1)
        if passed
        else round(random.uniform(81, 100), 1)
    )
    return passed, value_measured, "°C", None, 80


def motor_noise():
    passed = simulate_test_result(0.92)
    value_measured = (
        round(random.uniform(45, 50)) if passed else round(random.uniform(51, 55))
    )
    return passed, value_measured, "dB", None, 50


# Runs the motor at full speed
def final_rpm_reading():
    passed = simulate_test_result(1)
    value_measured = (
        round(random.uniform(2900, 3100))
        if passed
        else round(random.uniform(2500, 2900))
    )
    return passed, value_measured, "RPM", 2900, 3100


# Running Steps
def run_test(test, duration):
    start_time = datetime.now()
    passed, value_measured, unit, limit_low, limit_high = test()

    step = {
        "name": test.__name__,
        "started_at": start_time,
        "duration": duration,
        "step_passed": passed,
        "measurement_unit": unit,
        "measurement_value": value_measured,
        "limit_low": limit_low,
        "limit_high": limit_high,
    }
    return step


def run_all_tests():
    tests = [
        (visual_inspection_connector, timedelta(seconds=8)),
        (power_on_test, timedelta(seconds=1)),
        (power_supply_check_voltage, timedelta(seconds=3)),
        (power_supply_check_current, timedelta(seconds=3)),
        (motor_startup_test, timedelta(seconds=15)),
        (motor_startup_rpm, timedelta(seconds=20)),
        (speed_consistency_no_load_test, timedelta(seconds=10)),
        (encoder_feedback_measurement, timedelta(seconds=4)),
        (backlash_response_time_test, timedelta(seconds=6)),
        (full_speed_braking_test, timedelta(seconds=12)),
        (thermal_reading, timedelta(seconds=10)),
        (motor_noise, timedelta(seconds=18)),
        (encoder_feedback_test, timedelta(seconds=4)),
        (final_rpm_reading, timedelta(seconds=15)),
    ]

    steps = []

    for test, duration in tests:
        step = run_test(test, duration)
        steps.append(step)
        if not step["step_passed"]:
            break  # Stop the test execution if any step fails

    return steps


# Main function
def handle_test(end):
    for _ in range(end):
        # Generate a unique serial number for each Unit Under Test (UUT)
        part_number = "00109"
        revision = "A"
        static_segment = "4J"
        batch_number = "1024"
        random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
        serial_number = f"{part_number}{revision}{static_segment}{random_digits}"

        # Run all tests
        steps = run_all_tests()

        # Create a Run on TofuPilot
        client.create_run(
            procedure_id="FVT1",
            unit_under_test={
                "part_number": part_number,
                "revision": revision,
                "serial_number": serial_number,
                "batch_number": batch_number,
            },
            run_passed=all(step["step_passed"] for step in steps),
            steps=steps,
            report_variables={
                "motor_serial_number": serial_number,
                "production_date": str(datetime.now().strftime("%d.%m.%Y")),
                "report_date": str(datetime.now().strftime("%d.%m.%Y")),
            },
            attachments=["./motors/motor_connector.png"],
        )


# Run mock-up for multiple units
handle_test(10)
