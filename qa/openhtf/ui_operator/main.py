import openhtf as htf
from openhtf.plugs import user_input
from openhtf.plugs.user_input import UserInput
from tofupilot.openhtf import TofuPilot


def power_on(test):
    return htf.PhaseResult.CONTINUE


@htf.measures(
    htf.Measurement("led_color").with_validator(
        lambda color: color in ["Red", "Green", "Blue"]
    )
)
@htf.plug(user_input=UserInput)
def prompt_operator_led_color(test, user_input):
    led_color = user_input.prompt(message="What is the LED color? (Red/Green/Blue)")
    test.measurements.led_color = led_color


def main():
    test = htf.Test(
        power_on,
        prompt_operator_led_color,
        procedure_id="FVT2",
        part_number="00220D",
        revision="C",
    )
    with TofuPilot(test):
        test.execute(test_start=user_input.prompt_for_test_start())  # Prompt at start


if __name__ == "__main__":
    main()
