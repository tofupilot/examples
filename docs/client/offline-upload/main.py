from tofupilot import TofuPilotClient
from datetime import datetime, timedelta

client = TofuPilotClient()


def main():
    response = client.create_run(
        procedure_id="FVT1",
        started_at=datetime.now() - timedelta(days=1),  # Run performed the day before
        unit_under_test={
            "serial_number": "PCB1A001",
            "part_number": "PCB1",
        },
        run_passed=True,
    )
