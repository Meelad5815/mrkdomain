import io
import json
import unittest
from unittest.mock import patch

import gateway


class DummyHeaders(dict):
    def get(self, key, default=None):
        return super().get(key, default)


class DummyResponse:
    def __init__(self, body: bytes, status: int = 200, content_type: str = "text/plain"):
        self._body = body
        self.status = status
        self.headers = {"Content-Type": content_type}

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class GatewayProxyTests(unittest.TestCase):
    def _build_handler(self, host: str, path: str = "/"):
        handler = gateway.GatewayHandler.__new__(gateway.GatewayHandler)
        handler.headers = DummyHeaders({"Host": host, "Accept": "*/*", "User-Agent": "test"})
        handler.path = path
        handler.wfile = io.BytesIO()
        handler._sent = {}

        def send_response(code):
            handler._sent["code"] = code

        def send_header(key, value):
            handler._sent.setdefault("headers", {})[key] = value

        def end_headers():
            return None

        handler.send_response = send_response
        handler.send_header = send_header
        handler.end_headers = end_headers
        return handler

    @patch("gateway.urlopen")
    def test_proxy_success(self, mock_urlopen):
        mock_urlopen.return_value = DummyResponse(b"ok", 200, "text/plain")
        handler = self._build_handler("shop.mrk", "/")

        with patch.object(gateway.service, "resolve", return_value="http://127.0.0.1:9001"):
            handler._proxy()

        self.assertEqual(handler._sent["code"], 200)
        self.assertEqual(handler.wfile.getvalue(), b"ok")

    def test_proxy_missing_mapping(self):
        handler = self._build_handler("shop.mrk", "/")
        with patch.object(gateway.service, "resolve", return_value=None):
            handler._proxy()

        self.assertEqual(handler._sent["code"], 404)
        payload = json.loads(handler.wfile.getvalue().decode("utf-8"))
        self.assertIn("no mapping", payload["error"])


if __name__ == "__main__":
    unittest.main()
