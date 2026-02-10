from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from internal_naming import InternalNameService

service = InternalNameService()


class GatewayHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _host_name(self) -> str:
        host = self.headers.get("Host", "")
        return host.split(":", 1)[0].strip().lower()

    def _proxy(self) -> None:
        host_name = self._host_name()
        if not host_name:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "host header is required"})
            return

        try:
            target_base = service.resolve(host_name)
        except ValueError as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return

        if not target_base:
            self._json(HTTPStatus.NOT_FOUND, {"error": f"no mapping for host '{host_name}'"})
            return

        upstream_url = urljoin(target_base.rstrip("/") + "/", self.path.lstrip("/"))

        fwd_headers = {
            "User-Agent": self.headers.get("User-Agent", "mrk-gateway"),
            "Accept": self.headers.get("Accept", "*/*"),
            "X-Forwarded-Host": host_name,
            "X-Forwarded-Proto": "http",
        }
        request = Request(upstream_url, headers=fwd_headers, method="GET")

        try:
            with urlopen(request, timeout=10) as resp:
                body = resp.read()
                self.send_response(resp.status)
                content_type = resp.headers.get("Content-Type", "application/octet-stream")
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            self._json(exc.code, {"error": "upstream http error", "detail": detail})
        except URLError as exc:
            self._json(HTTPStatus.BAD_GATEWAY, {"error": "upstream not reachable", "detail": str(exc.reason)})

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json(HTTPStatus.OK, {"ok": True})
            return
        self._proxy()


def run(host: str = "0.0.0.0", port: int = 8080) -> None:
    server = ThreadingHTTPServer((host, port), GatewayHandler)
    print(f"Gateway listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
