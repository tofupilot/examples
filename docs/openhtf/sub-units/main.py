from openhtf import Test, PhaseResult
from tofupilot.openhtf import TofuPilot

# Create both units PCB1A001 and LEN1A001 before executing this script
# You can use example as docs/openhtf/procedures/main.py


def main():
    test = Test(
        procedure_id="FVT2",
        procedure_name="Camera Assembly",
        part_number="CAM1",
        sub_units=[{"serial_number": "PCB1A001"}, {"serial_number": "LEN1A001"}],
    )
    with TofuPilot(test):
        test.execute(lambda: "CAM1A001")


if __name__ == "__main__":
    main()
