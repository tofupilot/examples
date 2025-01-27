from tofupilot import TofuPilotClient


def main():
    client = TofuPilotClient()

    client.create_run(
        procedure_id="FVT1",
        unit_under_test={
            "serial_number": "PCB1A002",
            "part_number": "PCB1",
            "revision": "A",  # optional
            "batch_number": "12-24",  # optional
        },
        run_passed=True,
    )


if __name__ == "__main__":
    main()
