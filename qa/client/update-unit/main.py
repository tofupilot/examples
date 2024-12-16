from tofupilot import TofuPilotClient


def main():
    client = TofuPilotClient()

    client.update_unit(
        serial_number="00220B4K61222",
        sub_units=[
            {"serial_number": "SI0364A57283"},
        ],
    )


if __name__ == "__main__":
    main()
