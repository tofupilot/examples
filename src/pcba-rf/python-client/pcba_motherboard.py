from tofupilot import TofuPilotClient
from datetime import datetime, timedelta
import random

client = TofuPilotClient()


# Simulate FPY (First Pass Yield) for each step
def simulate_test_result(passed_prob):
    return random.random() < passed_prob


# Boolean Steps
def power_supply_test():
    passed = simulate_test_result(1)
    return passed, None, None, None, None


def ddr4_memory_check():
    passed = simulate_test_result(1)
    return passed, None, None, None, None


# Numeric Measurement Steps
def frequency_range_test():
    passed = simulate_test_result(0.99)
    value_measured = (
        round(random.uniform(100, 18000), 2)
        if passed
        else round(random.uniform(50, 99), 2)
    )  # To CHANGE
    return passed, value_measured, "MHz", 100, 18000


def bandwidth_test():
    passed = simulate_test_result(0.85)
    value_measured = (
        round(random.uniform(100, 18000), 2)
        if passed
        else round(random.uniform(50, 99), 2)
    )  # To CHANGE
    return passed, value_measured, "MHz", 100, 18000


def input_signal_power_test():
    passed = simulate_test_result(0.99)
    value_measured = (
        round(random.uniform(8, 12), 2) if passed else round(random.uniform(0, 7), 2)
    )
    return passed, value_measured, "dBm", None, 20


def output_signal_power_test():
    passed = simulate_test_result(0.99)
    value_measured = (
        round(random.uniform(8, 12), 2) if passed else round(random.uniform(0, 7), 2)
    )
    return passed, value_measured, "dBm", 7, 15


def adc_dac_resolution_check():
    passed = simulate_test_result(1)
    value_measured = "14 bits" if passed else "Incorrect Resolution"
    return passed, value_measured, None, None, None


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


# Execute all steps for the PCBA Motherboard Test
def run_all_tests():
    tests = [
        (power_supply_test, timedelta(seconds=10)),
        (frequency_range_test, timedelta(seconds=20)),
        (bandwidth_test, timedelta(seconds=15)),
        (input_signal_power_test, timedelta(seconds=20)),
        (output_signal_power_test, timedelta(seconds=15)),
        (adc_dac_resolution_check, timedelta(seconds=5)),
        (ddr4_memory_check, timedelta(seconds=30)),
    ]

    steps = []

    for test, duration in tests:
        step = run_test(test, duration)
        steps.append(step)
        if not step["step_passed"]:
            break

    return steps


# Manage the test execution and create a test run for each unit
def handle_test(end):
    with open("src/pcba-rf/serial_numbers.txt", "a") as f:
        for _ in range(end):
            random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
            serial_number = f"00375A4J{random_digits}"

            f.write(f"{serial_number}\n")

            failure_count = 0
            while True:
                steps = run_all_tests()
                run_passed = all(step["step_passed"] for step in steps)

                client.create_run(
                    procedure_id="FVT1",
                    unit_under_test={
                        "part_number": "00375",
                        "revision": "A",
                        "serial_number": serial_number,
                        "batch_number": "1024",
                    },
                    run_passed=run_passed,
                    steps=steps,
                )

                if run_passed or failure_count >= 5:
                    break
                else:
                    failure_count += 1


if __name__ == "__main__":
    handle_test(10)
