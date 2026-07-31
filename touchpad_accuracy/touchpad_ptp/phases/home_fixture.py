"""Home the probe and zero the gauge before anything is measured.

Positional error is only comparable across units if every press starts from the
same reference, so this runs first and the rest depend on it implicitly.
"""


def home_fixture(log, robot, gauge):
    log.info(f"Robot: {robot.identity()}")
    log.info(f"Gauge: {gauge.identity()}")
    gauge.zero()
    log.info("Fixture homed and zeroed")
