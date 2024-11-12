import sys
import subprocess
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Use the absolute path to the Python interpreter
            python_path = sys.executable
            result = subprocess.run(
                [python_path, "./templates/measurements.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            if result.returncode == 0:
                response_message = f"Script Output:\n{result.stdout}"
            else:
                response_message = (
                    f"Script encountered an error (Exit code {result.returncode}):\n"
                    f"{result.stderr}"
                )
            self.wfile.write(response_message.encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            error_message = f"Error executing script: {str(e)}"
            self.wfile.write(error_message.encode("utf-8"))
