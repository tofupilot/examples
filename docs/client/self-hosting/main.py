from tofupilot import TofuPilotClient
from datetime import datetime, timedelta


def main():
    client = TofuPilotClient(
        url="https://tofupilot.yourcompany.com"
    )  # specify URL here

    client.create_run(
        procedure_id="FVT1",
        procedure_name="PCB Testing",
        run_passed=True,
        unit_under_test={"serial_number": "PCB1A001", "part_number": "PCB1"},
        duration=timedelta(minutes=1, seconds=45),
    )


if __name__ == "__main__":
    main()
