from tofupilot import TofuPilotClient
from datetime import datetime, timedelta
import random
import uuid

client = TofuPilotClient()


# Simulate FPY for each step
def simulate_test_result(passed_prob):
    return random.random() < passed_prob


# Boolean Steps
def power_on_test():
    passed = simulate_test_result(1)
    return passed, None, None, None, None


def heat_up_start_test():
    passed = simulate_test_result(1)
    return passed, None, None, None, None


def target_temp_reached_test():
    passed = simulate_test_result(1)
    return passed, None, None, None, None


def cooling_system_activation_test():
    passed = simulate_test_result(1)
    return passed, None, None, None, None


def overheating_protection_test():
    passed = simulate_test_result(0.98)
    return passed, None, None, None, None


def cycle_completion_signal_test():
    passed = simulate_test_result(0.99)
    return passed, None, None, None, None


# Numeric Measurement Steps
def initial_temp_reading():
    passed = simulate_test_result(1)
    value_measured = (
        round(random.uniform(20, 25), 1) if passed else round(random.uniform(15, 19), 1)
    )
    return passed, value_measured, "°C", 20, 25


def temp_rise_rate_test():
    passed = simulate_test_result(0.74)
    value_measured = (
        round(random.uniform(5, 7), 2) if passed else round(random.uniform(3, 4.9), 2)
    )
    return passed, value_measured, "°C/min", 5, None


def stable_temp_test():
    passed = simulate_test_result(1)
    value_measured = (
        round(random.uniform(-1, 1), 2)
        if passed
        else round(random.uniform(1.1, 2.5), 2)
    )
    return passed, value_measured, "°C", -1, 1


def energy_consumption_test():
    passed = simulate_test_result(0.9)
    value_measured = (
        round(random.uniform(3, 5), 2) if passed else round(random.uniform(5, 6), 2)
    )
    return passed, value_measured, "kWh", None, 5


def cool_down_rate_test():
    passed = simulate_test_result(1)
    value_measured = (
        round(random.uniform(3, 4), 2) if passed else round(random.uniform(4.5, 5), 2)
    )
    return passed, value_measured, "°C/min", None, 4


def fan_speed_test():
    passed = simulate_test_result(1)
    value_measured = random.randint(1000, 1500) if passed else random.randint(800, 999)
    return passed, value_measured, "RPM", 1000, 1500


def noise_level_test():
    passed = simulate_test_result(0.99)
    value_measured = (
        round(random.uniform(55, 60), 1) if passed else round(random.uniform(60, 70), 1)
    )
    return passed, value_measured, "dB", None, 60


def final_temp_reading():
    passed = simulate_test_result(1)
    value_measured = (
        round(random.uniform(20, 25), 1) if passed else round(random.uniform(25, 30), 1)
    )
    return passed, value_measured, "°C", 20, 25


def operational_efficiency_test():
    passed = simulate_test_result(1)
    value_measured = (
        round(random.uniform(90, 95), 1) if passed else round(random.uniform(85, 89), 1)
    )
    return passed, value_measured, "%", 90, None


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
        (power_on_test, timedelta(seconds=1)),
        (initial_temp_reading, timedelta(seconds=2)),
        (heat_up_start_test, timedelta(seconds=1)),
        (temp_rise_rate_test, timedelta(seconds=3)),
        (target_temp_reached_test, timedelta(seconds=2)),
        (stable_temp_test, timedelta(seconds=10)),
        (energy_consumption_test, timedelta(seconds=5)),
        (cooling_system_activation_test, timedelta(seconds=1)),
        (cool_down_rate_test, timedelta(seconds=3)),
        (fan_speed_test, timedelta(seconds=2)),
        (overheating_protection_test, timedelta(seconds=2)),
        (noise_level_test, timedelta(seconds=2)),
        (cycle_completion_signal_test, timedelta(seconds=1)),
        (final_temp_reading, timedelta(seconds=2)),
        (operational_efficiency_test, timedelta(seconds=3)),
    ]

    steps = []

    for test, duration in tests:
        step = run_test(test, duration)
        steps.append(step)

    return steps


def handle_test(test_qty):
    for _ in range(test_qty):
        # Generate a unique serial number for each UUT (Unit Under Test)
        serial_number = str(uuid.uuid4())[:8]

        # Run all tests
        steps = run_all_tests()

        # Create a Run on TofuPilot
        client.create_run(
            procedure_id="FVT1",
            unit_under_test={
                "part_number": "UNIT42",
                "revision": "1.0",
                "serial_number": serial_number,
            },
            run_passed=all(step["step_passed"] for step in steps),
            steps=steps,
        )


if __name__ == "__main__":
    handle_test(10)
