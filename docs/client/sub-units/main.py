from tofupilot import TofuPilotClient

# Create both units PCB1A001 and LEN1A001 before executing this script
# You can use example as docs/openhtf/procedures/main.py


def main():
    client = TofuPilotClient()

    client.create_run(
        procedure_id="FVT2",
        procedure_name="Camera Assembly",
        unit_under_test={"serial_number": "CAM1A001", "part_number": "CAM1"},
        run_passed=True,
        sub_units=[{"serial_number": "PCB1A001"}, {"serial_number": "LEN1A001"}],
    )


if __name__ == "__main__":
    main()
