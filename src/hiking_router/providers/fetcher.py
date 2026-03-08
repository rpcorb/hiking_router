import json
import os
import socket
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class FetchError(Exception):
    pass


class FetchParseError(FetchError):
    pass


class FetchHTTPError(FetchError):
    pass


class FetchTimeout(FetchError):
    pass


class SourceUnavailableError(FetchError):
    pass


def parse_json_or_raise(payload: str) -> dict:
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise FetchParseError("Invalid JSON payload") from exc


def _network_disabled() -> bool:
    return os.environ.get("HIKING_ROUTER_DISABLE_NETWORK") == "1"


def http_get_text(url: str, timeout: int = 20, retries: int = 2) -> str:
    if _network_disabled():
        raise FetchTimeout("Network disabled by HIKING_ROUTER_DISABLE_NETWORK=1")
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urlopen(url, timeout=timeout) as response:
                return response.read().decode("utf-8")
        except HTTPError as exc:
            raise FetchHTTPError(f"HTTP {exc.code} for {url}") from exc
        except (TimeoutError, socket.timeout) as exc:
            last_error = exc
        except URLError as exc:
            last_error = exc
        if attempt < retries:
            time.sleep(0.25 * (2**attempt))
    raise FetchTimeout(f"Timeout or network error while fetching {url}") from last_error


def http_post_form_text(
    url: str, form_data: dict[str, str], timeout: int = 20, retries: int = 2
) -> str:
    if _network_disabled():
        raise FetchTimeout("Network disabled by HIKING_ROUTER_DISABLE_NETWORK=1")
    body = urlencode(form_data).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            request = Request(url, data=body, method="POST")
            request.add_header("Content-Type", "application/x-www-form-urlencoded")
            with urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8")
        except HTTPError as exc:
            raise FetchHTTPError(f"HTTP {exc.code} for {url}") from exc
        except (TimeoutError, socket.timeout) as exc:
            last_error = exc
        except URLError as exc:
            last_error = exc
        if attempt < retries:
            time.sleep(0.25 * (2**attempt))
    raise FetchTimeout(f"Timeout or network error while posting to {url}") from last_error


def http_get_bytes(url: str, timeout: int = 20, retries: int = 2) -> bytes:
    if _network_disabled():
        raise FetchTimeout("Network disabled by HIKING_ROUTER_DISABLE_NETWORK=1")
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urlopen(url, timeout=timeout) as response:
                return response.read()
        except HTTPError as exc:
            raise FetchHTTPError(f"HTTP {exc.code} for {url}") from exc
        except (TimeoutError, socket.timeout) as exc:
            last_error = exc
        except URLError as exc:
            last_error = exc
        if attempt < retries:
            time.sleep(0.25 * (2**attempt))
    raise FetchTimeout(f"Timeout or network error while fetching bytes from {url}") from last_error
