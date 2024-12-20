from openhtf import Test, PhaseResult
from tofupilot.openhtf import TofuPilot


def main():
    test = Test(
        procedure_id="FVT140",
        procedure_name="Camera Assembly",
        part_number="CAM1",
        sub_units=[{"serial_number": "PCB1A001"}, {"serial_number": "LEN1A001"}],
    )
    with TofuPilot(test):
        test.execute(lambda: "CAM1A001")


if __name__ == "__main__":
    main()
