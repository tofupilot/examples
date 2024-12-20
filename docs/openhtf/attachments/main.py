import openhtf as htf
from tofupilot.openhtf import TofuPilot


def step_file_attachment(test):
    test.attach_from_file(
        "data/temperature-map.png"
    )  # Replace with your actual file path
    return htf.PhaseResult.CONTINUE


def main():
    test = htf.Test(step_file_attachment, procedure_id="FVT1", part_number="PCB1")
    with TofuPilot(test):
        test.execute(lambda: "PCBA1A001")


if __name__ == "__main__":
    main()
