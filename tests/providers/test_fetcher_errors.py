import pytest
from hiking_router.providers.fetcher import parse_json_or_raise, FetchParseError


def test_parse_json_or_raise_raises_on_invalid_payload():
    with pytest.raises(FetchParseError):
        parse_json_or_raise("not-json")
