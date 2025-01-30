from tofupilot import TofuPilotClient, PhaseOutcome
from datetime import datetime, timedelta

client = TofuPilotClient()


def phase_one():
    start_time_millis = datetime.now().timestamp() * 1000
    phase = {
        "name": "phase_one",
        "outcome": PhaseOutcome.PASS,
        "start_time_millis": start_time_millis,
        "end_time_millis": start_time_millis
        + 30 * 1000,  # Indicating phase took 30 seconds to complete
    }
    return phase


def main():
    phases = [phase_one()]

    client.create_run(
        procedure_id="FVT1",
        unit_under_test={"serial_number": "PCB1A001", "part_number": "PCB1"},
        phases=phases,
        run_passed=all(phase["outcome"] == PhaseOutcome.PASS for phase in phases),
    )


if __name__ == "__main__":
    main()
