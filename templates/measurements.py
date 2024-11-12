import openhtf as htf
from openhtf.util import units
from tofupilot.openhtf import TofuPilot


def phase_one(test):
    return htf.PhaseResult.CONTINUE


@htf.measures(
    htf.Measurement("temperature").in_range(0, 100).with_units(units.DEGREE_CELSIUS)
)
def phase_temperature(test):
    test.measurements.temperature = 25


def main():
    test = htf.Test(phase_one, phase_temperature)
    with TofuPilot(test):  # just works™️
        test.execute(lambda: "PCB001")


if __name__ == "__main__":
    main()
