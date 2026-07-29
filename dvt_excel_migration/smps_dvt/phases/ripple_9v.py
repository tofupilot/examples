"""9V ripple: the two transcribed figures, plus the trace they came from."""

CH_9V = 2


def ripple_9v(measurements, scope):
    scope.configure_channel(CH_9V, 0.02)  # 20 mV/div
    scope.set_timebase(0.01)  # 10 ms/div: ~20 cycles of 100 Hz ripple
    scope.acquire()

    peak_mv, rms_mv = scope.measure_ripple(CH_9V)
    measurements.ripple_9v_peak_to_peak = peak_mv
    measurements.ripple_9v_rms = rms_mv

    times, values = scope.capture_waveform(CH_9V)
    measurements.ripple_9v_waveform.x_axis = times
    measurements.ripple_9v_waveform.y_axis.ripple = values
    # The same ceiling as the transcribed figure, checked against the trace.
    measurements.ripple_9v_waveform.y_axis.ripple.aggregations.peak_to_peak = (
        max(values) - min(values)
    )
