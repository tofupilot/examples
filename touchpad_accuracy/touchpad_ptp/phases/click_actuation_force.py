"""How hard the pad has to be pressed before it clicks.

Unrelated to position, but it comes off the same fixture in the same cycle, and
a dome that stiffens or softens is an early sign of the same mechanical problem
that moves the positional error.
"""


def click_actuation_force(measurements, gauge, log):
    grams = gauge.ramp_until_actuation()
    log.info(f"Switch actuated at {grams} g")

    measurements.actuation_force = grams
