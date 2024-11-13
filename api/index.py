from http.server import BaseHTTPRequestHandler
import json

from tofupilot import TofuPilotClient


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        # Handle preflight requests for CORS
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()

    def do_POST(self):
        # Add CORS headers
        self.send_header("Access-Control-Allow-Origin", "*")

        auth_header = self.headers.get("Authorization")
        if not auth_header:
            self.send_response(401)  # Unauthorized
            self.end_headers()
            self.wfile.write("Missing Authorization header".encode("utf-8"))
            return

        try:
            _, token = auth_header.split(" ")
        except ValueError:
            self.send_response(400)  # Bad Request
            self.end_headers()
            self.wfile.write("Invalid Authorization header format".encode("utf-8"))
            return

        # Read and parse the JSON body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        # Attempt to parse the JSON body, but treat it as optional
        try:
            body_data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            body_data = (
                {}
            )  # Default to an empty dictionary if the body is not valid JSON

        # Extract base_url, defaulting to None if not provided
        base_url = body_data.get("base_url", None)

        client = TofuPilotClient(api_key=token, base_url=base_url)

        client.create_run(
            procedure_id="FVT1",
            unit_under_test={"serial_number": "SN15", "part_number": "PN15"},
            run_passed=True,
        )

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hello, world!".encode("utf-8"))
        return
