import openhtf as htf
from tofupilot.openhtf import TofuPilot
from typing import Optional


# Create a successful test step
def step_one():
    return htf.PhaseResult.CONTINUE


def main(api_key: Optional[str], url: Optional[str]):
    # Set up test run for unit "00102" adding a single line before test execution
    test = htf.Test(step_one, procedure_id="FVT1", part_number="PCB01")
    with TofuPilot(test, api_key=api_key, url=url, stream=False):
        test.execute(lambda: "00102")
