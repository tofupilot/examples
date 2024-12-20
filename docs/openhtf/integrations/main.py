import openhtf as htf
from tofupilot.openhtf import TofuPilot  # Import OpenHTF for TofuPilot


def phase_one(test):
    return htf.PhaseResult.CONTINUE


def main():
    test = htf.Test(phase_one)
    with TofuPilot(test):  # One-line integration
        test.execute(lambda: "PCB001")


if __name__ == "__main__":
    main()
