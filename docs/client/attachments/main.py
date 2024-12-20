from tofupilot import TofuPilotClient


def step_file_attachment():
    file_path = ["data/temperature-map.png"]  # Replace with your actual files paths
    return file_path


def main():
    client = TofuPilotClient()

    attachments = step_file_attachment()

    client.create_run(
        procedure_id="FVT1",
        unit_under_test={"serial_number": "PCBA1A001", "part_number": "PCB1"},
        run_passed=True,
        attachments=attachments,
    )


if __name__ == "__main__":
    main()
