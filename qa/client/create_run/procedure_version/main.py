import random
import time

from tofupilot import TofuPilotClient


def main():
    client = TofuPilotClient()

    # Generate SN
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"SI0364A{random_digits}"

    # 1 Phase test
    start_time_millis = int(time.time() * 1000)
    voltage = round(random.uniform(3, 4), 1)
    limits = {"limit_low": 3.1, "limit_high": 3.5}
    passed = limits["limit_low"] <= voltage <= limits["limit_high"]
    outcome = {True: "PASS", False: "FAIL"}[passed]
    end_time_millis = int(time.time() * 1000)

    client.create_run(
        unit_under_test={
            "part_number": "SI0364A",
            "serial_number": serial_number,
        },
        procedure_name="PCBA Test",
        procedure_version="1.2.178",  # Can create a procedure version
        phases=[
            {
                "name": "test_voltage",
                "outcome": outcome,
                "start_time_millis": start_time_millis,
                "end_time_millis": end_time_millis,
                "measurements": [
                    {
                        "name": "voltage_input",
                        "outcome": outcome,
                        "measured_value": voltage,
                        "units": "V",
                        "lower_limit": limits["limit_low"],
                        "upper_limit": limits["limit_high"],
                    },
                ],
            },
        ],
        run_passed=passed,
    )


if __name__ == "__main__":
    main()
