from http.server import BaseHTTPRequestHandler
import json
import src.scripts.client as client
import src.scripts.openhtf as openhtf


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        # Handling preflight requests for CORS
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()

    def do_POST(self):
        auth_header = self.headers.get("Authorization")
        if not auth_header:
            self.send_response(401)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header(
                "Access-Control-Allow-Headers", "Authorization, Content-Type"
            )
            self.end_headers()
            self.wfile.write(b"Missing Authorization header")
            return

        try:
            _, api_key = auth_header.split(" ")
        except ValueError:
            self.send_response(400)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header(
                "Access-Control-Allow-Headers", "Authorization, Content-Type"
            )
            self.end_headers()
            self.wfile.write(b"Invalid Authorization header format")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        # Attempting to parse JSON body
        try:
            body_data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            body_data = {}

        url = body_data.get("url", None)
        framework = body_data.get("framework", "openhtf")

        # Calling the appropriate function based on the framework
        if framework == "client":
            client.simple(api_key, url)
        elif framework == "openhtf":
            openhtf.simple(api_key, url)

        # Sending a successful response
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()

        response_body = {"message": "Request processed successfully"}
        self.wfile.write(json.dumps(response_body).encode("utf-8"))
