from datetime import timedelta
from tofupilot import TofuPilotClient

from typing import Optional

def main(api_key: Optional[str], url: Optional[str]):

    # Initialize the TofuPilot client.
    client = TofuPilotClient(api_key=api_key, url=url)

    # Create a test run for the unit with serial number "00102" and part number "PCB01"
    client.create_run(
        procedure_id="FVT1",
        unit_under_test={"serial_number": "00102", "part_number": "PCB01"},
        run_passed=True,
        duration=timedelta(minutes=27, seconds=15),
    )
