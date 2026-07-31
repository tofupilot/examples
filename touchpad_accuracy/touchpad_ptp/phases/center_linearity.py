"""The nine targets a manual test taps by hand, as one curve.

Each target is a commanded coordinate; the measurement is the distance between
it and the contact the pad reported. Keeping the whole grid as a series means a
unit that is off in one corner is distinguishable from one that is off
everywhere, which a single worst-case number hides.
"""

import math

# 2 mm grid across the central region, clear of the edge band.
TARGETS = (
    (26, 16),
    (52, 16),
    (79, 16),
    (26, 32),
    (52, 32),
    (79, 32),
    (26, 49),
    (52, 49),
    (79, 49),
)


def center_linearity(measurements, robot, log):
    index = []
    errors = []

    for n, (target_x, target_y) in enumerate(TARGETS, start=1):
        reported_x, reported_y = robot.press(target_x, target_y)
        error = round(
            math.dist(
                (target_x, target_y), (reported_x, reported_y)), 3)

        log.info(
            f"({target_x},{target_y}) -> ({reported_x:.2f},{reported_y:.2f}) = {error} mm"
        )
        index.append(n)
        errors.append(error)

    measurements.center_positional_error.x_axis = index
    measurements.center_positional_error.y_axis.error = errors
    # The unit passes when every target is inside the limit, not on average.
    measurements.center_positional_error.y_axis.error.aggregations.max = max(
        errors)
    measurements.center_positional_error.y_axis.error.aggregations.mean = round(
        sum(errors) / len(errors), 3)
