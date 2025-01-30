import openhtf as htf
from tofupilot.openhtf import TofuPilot


def main():
    test = htf.Test(
        procedure_id="FVT1",
        procedure_name="PCB Testing",  # By default set as "openhtf_test"
        part_number="PCB1",
    )
    with TofuPilot(test):
        test.execute(lambda: "PCB1A001")  # Duration calculated during execution


if __name__ == "__main__":
    main()
