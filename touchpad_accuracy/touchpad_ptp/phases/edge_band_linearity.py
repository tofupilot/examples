"""The border, where touchpads actually fail.

Same press, same measurement as the central grid, but within 3.5 mm of an edge
the spec allows three times the error. Sampling the corners and the middle of
each side is what catches a sensor whose linearity falls apart only at one end.
"""

import math

# Targets inside the 3.5 mm border strip: four corners, four side midpoints.
TARGETS = (
    (2, 2),
    (52, 2),
    (103, 2),
    (2, 32),
    (103, 32),
    (2, 63),
    (52, 63),
    (103, 63),
)


def edge_band_linearity(measurements, robot, log):
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

    measurements.edge_positional_error.x_axis = index
    measurements.edge_positional_error.y_axis.error = errors
    measurements.edge_positional_error.y_axis.error.aggregations.max = max(
        errors)
    measurements.edge_positional_error.y_axis.error.aggregations.mean = round(
        sum(errors) / len(errors), 3
    )

    # Repeated as a scalar so the failing number is filterable on its own, and
    # so drift on the worst target is trendable across a population.
    measurements.worst_edge_error = max(errors)
