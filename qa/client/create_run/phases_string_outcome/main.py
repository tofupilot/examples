from tofupilot import TofuPilotClient
import random
import time

client = TofuPilotClient()


def simulate_test_result(yield_percentage):
    return random.random() < (yield_percentage / 100.0)


def battery_connection():
    passed = simulate_test_result(100)
    return passed, None, None, None, None


def check_voltage():
    passed = simulate_test_result(100)
    measured_value = (
        round(random.uniform(10.1, 12.0), 0)
        if passed
        else round(random.uniform(14.4, 15.0), 1)
    )
    return passed, measured_value, "V", None, 13


def check_soc():
    passed = simulate_test_result(95)
    measured_value = (
        round(random.uniform(50, 55), 0) if passed else round(random.uniform(20, 39), 2)
    )
    return passed, measured_value, "%", 40, 60


def check_soh():
    passed = simulate_test_result(100)
    measured_value = (
        round(random.uniform(96, 100), 0)
        if passed
        else round(random.uniform(70, 95), 2)
    )
    return passed, measured_value, "%", 95, None


def take_picture():
    passed = simulate_test_result(100)
    return passed, None, None, None, None


def flash_firmware():
    passed = simulate_test_result(90)
    measured_value = "1.2.4" if passed else "1.2.0"
    return passed, measured_value, None, None, None


# Running Tests
def run_test(test):
    start_time_millis = int(time.time() * 1000)

    passed, measured_value, unit, limit_low, limit_high = test()

    end_time_millis = int(time.time() * 1000)

    if passed == True:
        outcome = "PASS"
    elif passed == False:
        outcome = "FAIL"

    phase = {
        "name": test.__name__,  # Third phase
        "outcome": outcome,  # Outcome of the phase
        "start_time_millis": start_time_millis,
        "end_time_millis": end_time_millis,
        "measurements": [
            {
                "name": test.__name__,
                "outcome": outcome,
                "measured_value": measured_value,
                "units": unit,
                "lower_limit": limit_low,
                "upper_limit": limit_high,
            }
        ],
    }

    return phase


def run_all_tests():
    tests = [
        flash_firmware,
        battery_connection,
        check_voltage,
        check_soc,
        check_soh,
        take_picture,
    ]

    phases = []
    for test in tests:
        phase = run_test(test)
        phases.append(phase)

    return phases


def handle_test():
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"SI0364A{random_digits}"

    # Execute all tests
    phases = run_all_tests()

    client.create_run(
        procedure_id="FVT9",
        procedure_name="Test_QA",
        unit_under_test={
            "part_number": "SI03645A",
            "part_name": "PythonScript",
            "revision": "3.1",
            "batch_number": "11-24",
            "serial_number": serial_number,
        },
        run_passed=True,
        phases=phases,
    )


if __name__ == "__main__":
    for _ in range(1):
        handle_test()
