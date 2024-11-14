"""
Example demonstrating how to create a test run using OpenHTF.

This script initializes a test run for a unit with the serial number "00102" and part number "PCB01".
The test run is marked as successful (passed) with a single step.
"""

from typing import Optional

import openhtf as htf
from tofupilot.openhtf import TofuPilot


# Create a successful test step
def step_one():
    return htf.PhaseResult.CONTINUE


def simple(api_key: Optional[str], base_url: Optional[str]):
    # Set up test run for unit "00102" adding a single line before test execution
    test = htf.Test(step_one, procedure_id="FVT1", part_number="PCB01")
    with TofuPilot(test, api_key=api_key, base_url=base_url):
        test.execute(lambda: "00102")
