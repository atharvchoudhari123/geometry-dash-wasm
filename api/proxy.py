"""Vercel serverless version of the Geometry Dash Boomlings proxy."""
import os
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

ALLOWED_HOSTS = {"boomlings.com", "www.boomlings.com"}
TIMEOUT_SECONDS = 20


class handler(BaseHTTPRequestHandler):
    def _respond(self, status, body, content_type="text/plain; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _proxy(self):
        query = urllib.parse.urlparse(self.path).query
        target = urllib.parse.parse_qs(query).get("url", [""])[0]
        parsed = urllib.parse.urlparse(target)

        if (
            parsed.scheme not in ("http", "https")
            or parsed.hostname not in ALLOWED_HOSTS
            or parsed.username
            or parsed.password
            or parsed.port not in (None, 80, 443)
        ):
            self._respond(403, "host not allowed")
            return

        body = None
        headers = {"User-Agent": ""}
        if self.command == "POST":
            length = int(self.headers.get("Content-Length", "0") or 0)
            if length > 1024 * 1024:
                self._respond(413, "request too large")
                return
            body = self.rfile.read(length)
            headers["Content-Type"] = self.headers.get(
                "Content-Type", "application/x-www-form-urlencoded"
            )

        request = urllib.request.Request(
            target, data=body, headers=headers, method=self.command
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                self._respond(
                    response.status,
                    response.read(),
                    response.headers.get("Content-Type", "text/plain"),
                )
        except urllib.error.HTTPError as error:
            self._respond(
                error.code,
                error.read(),
                error.headers.get("Content-Type", "text/plain"),
            )
        except Exception as error:
            self._respond(502, "upstream error: " + str(error))

    def do_GET(self):
        self._proxy()

    def do_POST(self):
        self._proxy()

    def log_message(self, format, *args):
        # Avoid logging account request bodies or query strings.
        return
