"""
utils/api_client.py — Reusable API test client built on requests.Session.
Handles auth, retries, and clean JSON assertion helpers.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import requests
from requests import Response, Session

logger = logging.getLogger(__name__)


class ApiClient:
    """
    Thin wrapper around requests.Session.

    Features:
    - Auto-prepend base URL
    - Bearer token authentication
    - Response assertion helpers
    - Structured request/response logging

    Usage:
        client = ApiClient("https://api.your-app.com", "user", "pass")
        resp = client.get("/users/me")
        client.assert_status(resp, 200)
        data = client.json(resp)
    """

    def __init__(self, base_url: str, username: str = "",
                 password: str = "", token: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.session: Session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

        if token:
            self._set_token(token)
        elif username and password:
            self.authenticate(username, password)

    # ── Auth ──────────────────────────────────────────────────────────────────

    def authenticate(self, username: str, password: str) -> None:
        """POST /auth/login and store the returned Bearer token."""
        resp = self.post("/auth/login", json={"email": username, "password": password})
        data = resp.json()
        token = data.get("access_token") or data.get("token", "")
        if token:
            self._set_token(token)

    def _set_token(self, token: str) -> None:
        self.session.headers["Authorization"] = f"Bearer {token}"

    # ── HTTP verbs ────────────────────────────────────────────────────────────

    def get(self, path: str, **kwargs: Any) -> Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Response:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Response:
        return self._request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Response:
        return self._request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Response:
        return self._request("DELETE", path, **kwargs)

    def _request(self, method: str, path: str, **kwargs: Any) -> Response:
        url = self.base_url + path
        logger.debug("→ %s %s  payload=%s", method, url,
                     json.dumps(kwargs.get("json"), default=str))
        resp = self.session.request(method, url, **kwargs)
        logger.debug("← %s %s", resp.status_code, resp.text[:500])
        return resp

    # ── Assertion helpers ─────────────────────────────────────────────────────

    def assert_status(self, resp: Response, expected: int) -> Response:
        assert resp.status_code == expected, (
            f"Expected HTTP {expected}, got {resp.status_code}\n"
            f"URL: {resp.url}\nBody: {resp.text}"
        )
        return resp

    def assert_ok(self, resp: Response) -> Response:
        assert resp.ok, (
            f"Expected 2xx, got {resp.status_code}\n"
            f"URL: {resp.url}\nBody: {resp.text}"
        )
        return resp

    def json(self, resp: Response) -> dict[str, Any]:
        self.assert_ok(resp)
        return resp.json()

    def assert_field(self, resp: Response, field: str, expected: Any) -> Response:
        data = resp.json()
        actual = data.get(field)
        assert actual == expected, (
            f"Field '{field}': expected {expected!r}, got {actual!r}\n"
            f"Full body: {json.dumps(data, indent=2)}"
        )
        return resp

    def assert_schema(self, resp: Response, required_fields: list[str]) -> Response:
        data = resp.json()
        missing = [f for f in required_fields if f not in data]
        assert not missing, f"Missing fields in response: {missing}\nBody: {data}"
        return resp

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def close(self) -> None:
        self.session.close()
