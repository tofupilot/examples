from tofupilot import TofuPilotClient

client = TofuPilotClient()

client.create_run(
    procedure_id="FVT1",
    unit_under_test={
        "serial_number": "PCB1A001",
        "part_number": "PCB1",
        "revision": "A",  # optional
        "batch_number": "12-24",  # optional
    },
    run_passed=True,
)
