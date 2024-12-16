import openhtf as htf
from tofupilot.openhtf import TofuPilot
import time


# Create a successful test step
def step_one(test):
    time.sleep(5)
    return htf.PhaseResult.CONTINUE


def step_two(test):
    time.sleep(1)
    return htf.PhaseResult.CONTINUE


def step_three(test):
    time.sleep(1)
    return htf.PhaseResult.CONTINUE


def step_four(test):
    time.sleep(1)
    return htf.PhaseResult.CONTINUE


def step_five(test):
    time.sleep(1)
    return htf.PhaseResult.CONTINUE


# Set up test run for unit "00102" adding a single line before test execution
def main(serial_number):
    test = htf.Test(
        step_one,
        step_two,
        step_three,
        step_four,
        step_five,
        procedure_id="FVT1",
        part_number="PCB01",
    )

    with TofuPilot(test):
        test.execute(lambda: serial_number)


if __name__ == "__main__":
    for i in range(3):
        serial_number = "aaa" + str(i).zfill(5)
        main(serial_number)
