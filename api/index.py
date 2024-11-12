from http.server import BaseHTTPRequestHandler

import openhtf as htf
from openhtf.util import units
from tofupilot.openhtf import TofuPilot


def phase_one(test):
    return htf.PhaseResult.CONTINUE


@htf.measures(
    htf.Measurement("temperature").in_range(0, 100).with_units(units.DEGREE_CELSIUS)
)
def phase_temperature(test):
    test.measurements.temperature = 25


def main():
    test = htf.Test(phase_one, phase_temperature)
    with TofuPilot(test):  # just works
        test.execute(lambda: "PCB001")


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        main()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hello, world!".encode("utf-8"))
        return
