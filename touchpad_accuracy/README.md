# Touchpad positional accuracy

A touchpad is tested by pressing it. A robot puts a known force on a known
coordinate, and the pad reports where it thinks it was touched; the number that
matters is the distance between the two.

`touchpad_ptp/` records that distance against the Precision Touchpad linearity
limits — **0.5 mm** across the pad, relaxed to **1.5 mm** within 3.5 mm of an
edge, where the sensor is least linear. Windows reports these distances in
himetric units (0.01 mm), which is what the HID read in `plugs/touch_robot.py`
converts from.

```
touchpad_ptp/
├── procedure.yaml          phases, measurements and limits
├── phases/                 the Python each phase runs
└── plugs/                  one class per instrument
```

```bash
tofupilot run ./touchpad_ptp
```

The plugs return representative data so the procedure runs anywhere. Every
method keeps its real call directly above, commented out — swap the two and the
same procedure drives the bench:

- `plugs/touch_robot.py` — motion controller over VISA for the press, HID
  digitizer report for the contact the pad reported
- `plugs/force_gauge.py` — load cell ramped until the dome switch closes,
  triggered on the closure rather than sampled and compared afterwards

## The grid is one measurement, not nine

A manual test taps each target and writes down whether it looked right. Here
each grid becomes a curve indexed by target, with `max` validated against the
spec limit and `mean` against a tighter working limit:

```yaml
- name: Edge Positional Error
  x_axis:
    legend: Target
  y_axis:
    - legend: Error
      unit: mm
      aggregations:
        - type: max
          validators:
            - operator: "<="
              expected_value: 1.5
```

`max` is what fails the unit — one target outside the limit is a failure no
average should absorb. Keeping the whole series alongside it is what separates
a pad that is off in one corner from one that is off everywhere, which is the
difference between a fixture problem and a sensor problem.

The worst edge target is recorded a second time as a scalar, so the failing
number is filterable on its own and trendable across a population.

## Two limits, one press

The central grid and the edge band run the same code against the same fixture.
They are separate phases only because the spec allows three times the error
inside the border strip, and a single limit would either pass a bad centre or
fail a good edge.

Click actuation force comes off the same fixture in the same cycle. It has
nothing to do with position, but a dome that stiffens or softens is an early
sign of the same mechanical drift that moves the positional error, and it costs
one extra phase to catch.
