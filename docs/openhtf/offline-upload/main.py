from tofupilot import TofuPilotClient

client = TofuPilotClient()


def main():
    file_path = "data/SI03645A27619.openhtf_test.2025-01-20_15-32-06-058.json"  # Replace the path to your report
    client.create_run_from_openhtf_report(file_path)


if __name__ == "__main__":
    main()
