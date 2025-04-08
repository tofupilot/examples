"""
Basic example showing how to create a test run with logs using the TofuPilotClient.

This script creates a test run for a unit with the specified serial number and part number,
indicating whether the test passed.
Logs are handled using a custom handler.

Ensure your API key is stored in the environment variables as per the documentation:
https://tofupilot.com/docs/user-management#api-key
"""
import logging
import sys
from tofupilot import TofuPilotClient

class JsonCaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        log_entry = {
            "level": record.levelname,
            "timestamp": int(record.created * 1000),
            "message": record.getMessage(),
            # optional
            "source_file": record.filename,
            # optional
            "line_number": record.lineno,
        }
        self.logs.append(log_entry)


# Initialize the TofuPilot client.
client = TofuPilotClient()

# Set up local logger
local_logger = logging.getLogger("test_logger")
local_logger.setLevel(logging.DEBUG)
local_logger.propagate = (
    False  # if we don't want to propagate to the parent/root logger
)

capture_handler = JsonCaptureHandler()
output_handler = logging.StreamHandler(sys.stdout)
local_logger.addHandler(capture_handler)
local_logger.addHandler(output_handler)


local_logger.warning("This is a log we want to keep.")

# Create a run and send logs
try:
    client.create_run(
        procedure_id="Logs1",
        procedure_name="LOGS",
        unit_under_test={"serial_number": "00007035", "part_number": "LOGS01"},
        run_passed=True,
        logs=capture_handler.logs,
    )
finally:
    local_logger.removeHandler(capture_handler)