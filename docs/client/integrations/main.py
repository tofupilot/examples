from tofupilot import TofuPilotClient

client = TofuPilotClient()

client.create_run(
    procedure_id="FVT1",  # Define the TofuPilot's procedure ID
    unit_under_test={
        "serial_number": "PCB1A001",
        "part_number": "PCB1",
    },
    run_passed=True,  # Set the Run status to Pass
)
