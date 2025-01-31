import random
from datetime import timedelta, datetime
from tofupilot import TofuPilotClient, PhaseOutcome, MeasurementOutcome


def calculate_measurement_outcome(value, lower_limit, upper_limit):
    if (lower_limit is not None and value < lower_limit) or (
        upper_limit is not None and value > upper_limit
    ):
        return MeasurementOutcome.FAIL
    return MeasurementOutcome.PASS


def setup_battery_test():
    return {}


def flash_firmware_and_check_version():
    return {"firmware_version": ("prod_2.5.1", None, None, None)}


def configure_gauge_parameters():
    return {
        "gauge_syspress": (True, None, None, None),
        "calibration_current_CCGain": (3.631, None, None, None),
    }


def measure_battery_state():
    return {
        "input_voltage": (round(random.uniform(3.1, 3.6), 2), "V", 3.1, 3.5),
        "output_current": (round(random.uniform(0.5, 0.660), 3), "A", None, 0.655),
        "state_of_health": (round(random.uniform(0.94, 0.99), 2), "%", 0.95, None),
    }


# Créer la phase en intégrant les tests
def create_phase(test_function):
    test = test_function()
    measurements = []
    phase_outcome = PhaseOutcome.PASS
    start_time_millis = datetime.now().timestamp() * 1000

    # Évaluer chaque mesure et son outcome
    for measure_name, (value, unit, lower, upper) in test.items():
        outcome = calculate_measurement_outcome(value, lower, upper)
        measurements.append(
            {
                "name": measure_name,
                "measured_value": value,
                "units": unit,
                "outcome": outcome,
                "lower_limit": lower,
                "upper_limit": upper,
            }
        )
        if outcome == MeasurementOutcome.FAIL:
            phase_outcome = PhaseOutcome.FAIL

    # Retourner la phase avec son outcome et les mesures
    return {
        "name": test_function.__name__,
        "outcome": phase_outcome,
        "start_time_millis": start_time_millis,
        "end_time_millis": start_time_millis + 3000,
        "measurements": measurements,
    }


# Fonction principale pour exécuter toutes les phases
def main():
    # Liste des phases de test
    tests = [
        setup_battery_test,
        flash_firmware_and_check_version,
        configure_gauge_parameters,
        measure_battery_state,
    ]

    # Initialiser le client TofuPilot
    client = TofuPilotClient()

    # Générer les phases à partir des tests
    phases = [create_phase(test) for test in tests]

    # Créer le run dans TofuPilot
    client.create_run(
        procedure_name="Battery PCBA Testing",
        procedure_id="FVT1",
        unit_under_test={
            "serial_number": f"PCB01A{random.randint(100, 999)}",
            "part_number": "PCB01",
            "part_name": "Battery PCBA Motherboard",
            "revision": "A",
            "batch_number": "12-24",
        },
        phases=phases,
        run_passed=all(phase["outcome"] == PhaseOutcome.PASS for phase in phases),
    )


if __name__ == "__main__":
    main()
