import json


class FetchError(Exception):
    pass


class FetchParseError(FetchError):
    pass


def parse_json_or_raise(payload: str) -> dict:
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise FetchParseError("Invalid JSON payload") from exc
