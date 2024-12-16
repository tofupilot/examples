from tofupilot import TofuPilotClient


def main():
    client = TofuPilotClient()

    client.delete_run(run_id="e2668a2c-800c-11ef-96d8-43774a4ee6c2")

    client.delete_unit(
        serial_number="00143B4J67607",
    )


if __name__ == "__main__":
    main()
