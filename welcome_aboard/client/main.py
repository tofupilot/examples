from datetime import datetime
from tofupilot import TofuPilotClient, PhaseOutcome, MeasurementOutcome
import random


def simulate_test_result(yield_percentage):
    return random.random() < yield_percentage


def setup_and_connect():
    return True, [
        {
            "name": "connection_status",
            "value": True,
            "units": None,
            "lower_limit": None,
            "upper_limit": None,
        }
    ]


def flash_production_firmware():
    return True, [
        {
            "name": "firmware_version",
            "value": "prod_2.5.1",
            "units": None,
            "lower_limit": None,
            "upper_limit": None,
        }
    ]


def configuration_battery_gauge():
    gauge_syspress = True
    calibration_voltage = 12133
    calibration_current = 3.631
    calibration_temperature = "on"

    return True, [
        {
            "name": "gauge_syspress",
            "value": gauge_syspress,
            "units": None,
            "lower_limit": None,
            "upper_limit": None,
        },
        {
            "name": "calibration_voltage",
            "value": calibration_voltage,
            "units": "mV",
            "lower_limit": 12000,
            "upper_limit": 12500,
        },
        {
            "name": "calibration_current",
            "value": calibration_current,
            "units": "A",
            "lower_limit": 3.5,
            "upper_limit": 4.0,
        },
        {
            "name": "calibration_temperature",
            "value": calibration_temperature,
            "units": None,
            "lower_limit": None,
            "upper_limit": None,
        },
    ]


def phase_voltage_measurements():
    passed = simulate_test_result(0.85)
    input_voltage = (
        round(random.uniform(3.1, 3.5), 1)
        if passed
        else round(random.uniform(0, 0.010), 3)
    )
    output_voltage = round(random.uniform(1.2, 1.3), 1) if passed else 0
    output_current = (
        round(random.uniform(0.5, 0.655), 3)
        if passed
        else round(random.uniform(0, 0.010), 3)
    )
    state_of_health = round(random.uniform(0.95, 0.98), 2)

    return passed, [
        {
            "name": "input_voltage",
            "value": input_voltage,
            "units": "V",
            "lower_limit": 3.1,
            "upper_limit": 3.5,
        },
        {
            "name": "output_voltage",
            "value": output_voltage,
            "units": "V",
            "lower_limit": 1.1,
            "upper_limit": 1.3,
        },
        {
            "name": "output_current",
            "value": output_current,
            "units": "A",
            "lower_limit": 0.5,
            "upper_limit": 0.655,
        },
        {
            "name": "state_of_health",
            "value": state_of_health,
            "units": None,
            "lower_limit": 0.95,
            "upper_limit": 0.98,
        },
    ]


def ir_test():
    internal_resistance_value = round(random.uniform(0.007, 0.012), 3)
    return True, [
        {
            "name": "internal_resistance",
            "value": internal_resistance_value,
            "units": "Ω",
            "lower_limit": 0.005,
            "upper_limit": 0.015,
        }
    ]


def run_test(test, duration):
    start_time = datetime.now().timestamp()

    passed, measurements = test()

    phase = {
        "name": test.__name__,
        "outcome": PhaseOutcome.PASS if passed else PhaseOutcome.FAIL,
        "start_time_millis": start_time,
        "end_time_millis": start_time + duration,
        "measurements": [
            {
                "name": measurement["name"],
                "outcome": (
                    MeasurementOutcome.PASS
                    if (
                        measurement["lower_limit"] is None
                        or measurement["upper_limit"] is None
                        or (
                            measurement["lower_limit"]
                            <= measurement["value"]
                            <= measurement["upper_limit"]
                        )
                    )
                    else MeasurementOutcome.FAIL
                ),
                "measured_value": measurement["value"],
                "units": measurement["units"],
                "lower_limit": measurement["lower_limit"],
                "upper_limit": measurement["upper_limit"],
            }
            for measurement in measurements
        ],
    }
    return phase


def run_all_tests():
    tests = [
        (setup_and_connect, 8 * 1000),  # duration in seconds
        (flash_production_firmware, 3 * 1000),
        (configuration_battery_gauge, 12 * 1000),
        (phase_voltage_measurements, 10 * 1000),
        (ir_test, 4 * 1000),
    ]

    phases = []
    for test, duration in tests:
        phase = run_test(test, duration)
        phases.append(phase)

    return phases


def main():
    # Initialize the TofuPilot client.
    client = TofuPilotClient()

    random_digits = "".join([str(random.randint(0, 9)) for _ in range(3)])
    serial_number = f"PCB01A{random_digits}"

    # Execute all phases in this test
    phases = run_all_tests()

    client.create_run(
        procedure_id="FVT1",
        procedure_name="Battery PCBA Testing",
        unit_under_test={
            "serial_number": serial_number,
            "part_number": "PCB01",
            "part_name": "Battery PCBA Motherboard",
            "revision": "A",
            "batch_number": "12-24",
        },
        run_passed=all(phase["outcome"] == PhaseOutcome.PASS for phase in phases),
        phases=phases,
    )


if __name__ == "__main__":
    main()
