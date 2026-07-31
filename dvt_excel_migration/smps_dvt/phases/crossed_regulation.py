"""Both rails at nominal input: one row of the report."""

CH_23V, CH_9V = 1, 2


def crossed_regulation(measurements, scope, ac_source):
    ac_source.set_voltage(230)
    scope.configure_channel(CH_23V, 5.0)
    scope.configure_channel(CH_9V, 2.0)

    measurements.rail_23v = scope.measure_dc(CH_23V)
    measurements.rail_9v = scope.measure_dc(CH_9V)
