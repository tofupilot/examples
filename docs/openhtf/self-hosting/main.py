import openhtf as htf
from tofupilot.openhtf import TofuPilot


def main():
    test = htf.Test(
        procedure_id="FVT1",
        procedure_name="PCB Testing",
        part_number="PCB1",
    )
    with TofuPilot(test, url="https://tofupilot.yourcompany.com"):  # specify URL here
        test.execute(lambda: "PCB1A001")


if __name__ == "__main__":
    main()
