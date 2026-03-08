import pytest


@pytest.fixture(autouse=True)
def disable_network_for_tests(monkeypatch):
    # Keep tests deterministic and fast by preventing live HTTP calls.
    monkeypatch.setenv("HIKING_ROUTER_DISABLE_NETWORK", "1")
