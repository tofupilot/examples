# DVT Excel migration

Moving a design-verification report out of a spreadsheet and onto the bench, in
two steps.

## Step 1 — Import the reports you already have

`xcu_import.py` reads a DVT workbook and creates one TofuPilot run from it.

TofuPilot imports Excel natively, but two shapes common in hand-written reports
defeat the column mapper:

- **Stacked cells.** A cell holding `22.33 - 10.11 / 22.34 - 10.10 / 22.35 - 10.11`
  is three samples of a two-rail measurement, not one value.
- **Embedded plots.** Screenshots live in the drawing layer, so a mapper that
  reads cells never sees them. Their anchor row is what ties a plot to the test
  it proves.

The script flattens both: it expands stacked cells to one measurement per
sample per temperature block, and pulls the images out of the `.xlsx` zip keyed
by anchor row.

```bash
pip install tofupilot openpyxl
export TOFUPILOT_API_KEY=...

python xcu_import.py "DVT report.xlsx" \
    --procedure-id <uuid> \
    --serial-number SN-0001 \
    --part-number PCB-REV-A
```

Add `--dry-run` to see what it would create without uploading, and
`--waveforms <dir>` to promote curves to multi-dimensional measurements when
scope CSVs are available (named `<testnr>_<sample>.csv`).

On a real 5-sheet report this produced one run with 13 phases, 111
measurements and 49 attached plots in about 30 seconds.

## Step 2 — Stop writing the report

`smps-dvt/` is the same tests as a TofuPilot procedure, so values are captured
as they are measured rather than read off a screen and typed into a sheet.

```
smps-dvt/
├── procedure.yaml          phases, measurements and limits
├── phases/                 the Python each phase runs
└── plugs/                  one class per instrument
```

```bash
tofupilot run ./smps-dvt
```

The plugs return representative data so the procedure runs anywhere. Every
method keeps its real SCPI call directly above, commented out — swap the two
and the same procedure drives the bench:

- `plugs/scope.py` — Tektronix MSO5-series, 12-bit High Res, AC-coupled ripple
  with a 20 MHz bandwidth limit, `CURVe?` waveform readback with
  `YMUlt`/`YOFf`/`YZEro`/`XINcr` scaling
- `plugs/ac_source.py` — programmable AC source for the mains sweep

What the spreadsheet cannot do:

- The eleven crossed-regulation rows become **one sweep**, recorded as a
  regulation curve indexed by input voltage, with `min`/`max` aggregations
  validated against the rail limits.
- Each ripple test keeps **the waveform itself**, not a picture of it, and the
  400 mV ceiling is checked against the trace rather than a transcribed number.

Because the curve is data, the same measurement stays comparable across samples
and across temperature setpoints. Run one per chamber setpoint and the drift is
visible directly.
