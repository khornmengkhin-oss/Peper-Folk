"""Local web connection. Run: python3 server.py. No external packages required."""
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import json
import os
import hmac
import argparse

import database
import restaurant

WEB = Path(__file__).with_name("web")
STAFF_PIN = os.environ.get("RESTAURANT_PIN", "2468")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def json_response(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def check_pin(self):
        return hmac.compare_digest(self.headers.get("X-Staff-Pin", ""), STAFF_PIN)

    def do_GET(self):
        url = urlparse(self.path)
        if not url.path.startswith("/api/"):
            return super().do_GET()
        if url.path.startswith("/api/staff/") and not self.check_pin():
            return self.json_response({"error": "Enter the staff PIN."}, 401)
        query = parse_qs(url.query)
        try:
            if url.path == "/api/menu":
                return self.json_response(restaurant.get_menu())
            if url.path == "/api/track":
                order = restaurant.track_order(query.get("ref", [""])[0])
                return self.json_response(order if order else {"error": "Order not found."}, 200 if order else 404)
            if url.path == "/api/staff/orders":
                return self.json_response(restaurant.staff_orders())
            if url.path == "/api/staff/report":
                return self.json_response(restaurant.sales_report(query.get("date", [restaurant.now()[:10]])[0]))
            return self.json_response({"error": "Not found."}, 404)
        except ValueError as error:
            return self.json_response({"error": str(error)}, 400)

    def do_POST(self):
        url = urlparse(self.path)
        if url.path.startswith("/api/staff/") and not self.check_pin():
            return self.json_response({"error": "Enter the staff PIN."}, 401)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 100_000:
                raise ValueError("Invalid request size.")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("Invalid request.")
            if url.path == "/api/orders":
                return self.json_response(restaurant.place_order(data), 201)
            if url.path == "/api/staff/status":
                return self.json_response(restaurant.change_status(data.get("reference"), data.get("status")))
            if url.path == "/api/staff/availability":
                restaurant.change_availability(data.get("id"), data.get("available"))
                return self.json_response({"success": True})
            return self.json_response({"error": "Not found."}, 404)
        except (ValueError, TypeError, UnicodeError) as error:
            return self.json_response({"error": str(error)}, 400)


if __name__ == "__main__":
    database.initialize()
    parser = argparse.ArgumentParser(description="Run the local restaurant demo.")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    parser.add_argument("--host", choices=["127.0.0.1", "localhost"], default="127.0.0.1")
    parser.add_argument("--strictPort", action="store_true")
    options = parser.parse_args()
    port = options.port
    print(f"Mekong & Fork is running at http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
