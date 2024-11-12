from http.server import BaseHTTPRequestHandler

from tofupilot import TofuPilotClient


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        auth_header = self.headers.get("Authorization")
        _, token = auth_header.split(" ")

        client = TofuPilotClient(api_key=token, base_url="http://localhost:3000")

        client.create_run(procedure_id="FVT1", serial_number="SN15", part_number="PN15")

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hello, world!".encode("utf-8"))
        return
