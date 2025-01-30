import openhtf as htf
from tofupilot.openhtf import TofuPilot


def step_one(test):  # Step name is the function name
    return htf.PhaseResult.CONTINUE  # Pass status


def main():
    test = htf.Test(step_one, procedure_id="FVT1", part_number="PCB1")
    with TofuPilot(test):
        test.execute(
            lambda: "PCB1A001"
        )  # duration and started_at are set automatically


if __name__ == "__main__":
    main()
