"""The rows a report fills in one at a time, as a single sweep.

Each rail becomes a curve indexed by input voltage, so regulation is something
to compare across samples rather than a column of numbers to read.
"""

# Nominal 230 Vac +/-10%.
MAINS_SWEEP_VAC = (207, 216, 230, 244, 253)

CH_23V, CH_9V = 1, 2


def crossed_regulation_sweep(measurements, scope, ac_source):
    mains = []
    rail_23v = []
    rail_9v = []

    for volts in MAINS_SWEEP_VAC:
        ac_source.set_voltage(volts)
        mains.append(volts)
        rail_23v.append(scope.measure_dc(CH_23V))
        rail_9v.append(scope.measure_dc(CH_9V))

    measurements.rail_23v_vs_mains.x_axis = mains
    measurements.rail_23v_vs_mains.y_axis.rail_23v = rail_23v
    # The sweep passes when the rail stays inside its limits at every point.
    measurements.rail_23v_vs_mains.y_axis.rail_23v.aggregations.min = min(
        rail_23v)
    measurements.rail_23v_vs_mains.y_axis.rail_23v.aggregations.max = max(
        rail_23v)

    measurements.rail_9v_vs_mains.x_axis = mains
    measurements.rail_9v_vs_mains.y_axis.rail_9v = rail_9v
    measurements.rail_9v_vs_mains.y_axis.rail_9v.aggregations.min = min(
        rail_9v)
    measurements.rail_9v_vs_mains.y_axis.rail_9v.aggregations.max = max(
        rail_9v)

    ac_source.set_voltage(230)
