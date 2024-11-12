from http.server import BaseHTTPRequestHandler

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
        _, token = auth_header.split(" ")

        client = TofuPilotClient(api_key=token, base_url="http://localhost:3000")

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
