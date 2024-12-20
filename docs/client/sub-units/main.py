from tofupilot import TofuPilotClient

client = TofuPilotClient()

client.create_run(
    procedure_id="FVT2",
    procedure_name="Camera Assembly",
    unit_under_test={"serial_number": "CAM1A001", "part_number": "CAM1"},
    run_passed=True,
    sub_units=[{"serial_number": "PCB1A001"}, {"serial_number": "LEN1A001"}],
)
