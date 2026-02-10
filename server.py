from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from internal_naming import InternalNameService

service = InternalNameService()


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self._send_json(HTTPStatus.OK, {"ok": True})
            return

        if parsed.path == "/names":
            self._send_json(HTTPStatus.OK, {"items": service.all_names()})
            return

        if parsed.path == "/resolve":
            name = parse_qs(parsed.query).get("name", [None])[0]
            if not name:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "query param 'name' is required"})
                return

            try:
                target = service.resolve(name)
            except ValueError as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return

            if target is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "name not found"})
                return

            self._send_json(HTTPStatus.OK, {"name": name.lower(), "target": target})
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "route not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/register":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "route not found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid json"})
            return

        name = payload.get("name")
        target = payload.get("target")
        try:
            service.register(name=name, target=target)
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return

        self._send_json(
            HTTPStatus.CREATED,
            {"message": "registered", "name": name.lower(), "target": target.strip()},
        )


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Private name service listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
