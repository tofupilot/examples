import random
from datetime import datetime, timedelta

from tofupilot import TofuPilotClient

client = TofuPilotClient()


def simulate_test_result(yield_percentage):
    return random.random() < (yield_percentage / 100.0)


def battery_connection():
    passed = simulate_test_result(100)
    return passed, None, None, None, None


def check_voltage():
    passed = simulate_test_result(100)
    value_measured = (
        round(random.uniform(10.1, 12.0), 0)
        if passed
        else round(random.uniform(14.4, 15.0), 1)
    )
    return passed, value_measured, "V", None, 13


def check_soc():
    passed = simulate_test_result(95)
    value_measured = (
        round(
            random.uniform(
                50,
                55),
            0) if passed else round(
            random.uniform(
                20,
                39),
            2))
    return passed, value_measured, "%", 40, 60


def check_soh():
    passed = simulate_test_result(100)
    value_measured = (
        round(random.uniform(96, 100), 0)
        if passed
        else round(random.uniform(70, 95), 2)
    )
    return passed, value_measured, "%", 95, None


def take_picture():
    passed = simulate_test_result(100)
    return passed, None, None, None, None


def flash_firmware():
    passed = simulate_test_result(90)
    value_measured = "1.2.4" if passed else "1.2.0"
    return passed, value_measured, None, None, None


# Running Tests
def run_test(test, duration):
    start_time = datetime.now() - timedelta(days=1)
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
        (flash_firmware, timedelta(minutes=3, seconds=32)),
        (battery_connection, timedelta(seconds=8)),
        (check_voltage, timedelta(seconds=3)),
        (check_soc, timedelta(seconds=1)),
        (check_soh, timedelta(seconds=5)),
        (take_picture, timedelta(seconds=12)),
    ]

    steps = []
    total_duration = timedelta(0)

    for test, duration in tests:
        step = run_test(test, duration)
        steps.append(step)
        total_duration += duration

    return steps, total_duration


def handle_test():
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"SI0364A{random_digits}"

    # Exécuter tous les tests
    steps, total_duration = run_all_tests()

    # Créer un rapport de test
    client.create_run(
        procedure_id="FVT9",
        # procedure_name="olé",
        unit_under_test={
            "part_number": "SI03ddd64A",
            "revision": "3.1",
            "batch_number": "12-24",
            "serial_number": serial_number,
        },
        run_passed=all(step["step_passed"] for step in steps),
        started_at=datetime.now() - timedelta(days=1),
        steps=steps,
    )


if __name__ == "__main__":
    handle_test()
