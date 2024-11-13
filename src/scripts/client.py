"""
Example demonstrating how to create a test run using the TofuPilotClient.

This script initializes a test run for a unit with the serial number "00102" and part number "PCB01".
The test run is marked as successful (passed).
"""

from typing import Optional
from datetime import timedelta
from tofupilot import TofuPilotClient


def simple(api_key: Optional[str], base_url: Optional[str]):

    # Initialize the TofuPilot client.
    client = TofuPilotClient(api_key=api_key, base_url=base_url)

    # Create a test run for the unit with serial number "00102" and part number "PCB01"
    client.create_run(
        procedure_id="FVT1",
        unit_under_test={"serial_number": "00102", "part_number": "PCB01"},
        run_passed=True,
        duration=timedelta(minutes=27, seconds=15),
    )
