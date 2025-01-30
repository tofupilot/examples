from tofupilot import TofuPilotClient
from datetime import datetime


def get_unit_under_test():
    return {"serial_number": "PCB1A001", "batch_number": "1024"}


def main():
    client = TofuPilotClient()

    uut = get_unit_under_test()

    client.create_run(
        procedure_id="FVT1",
        unit_under_test={
            "serial_number": uut["serial_number"],
            "part_number": "PCB1",
            "batch_number": uut["batch_number"],
        },
        run_passed=True,
        report_variables={
            "motor_serial_number": uut["serial_number"],
            "motor_batch_number": uut["batch_number"],
            "production_date": str(datetime.now().strftime("%d.%m.%Y")),
            "report_date": str(datetime.now().strftime("%d.%m.%Y")),
            "safety_test_status": "Passed",
        },
    )


if __name__ == "__main__":
    main()
