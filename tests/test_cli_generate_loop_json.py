import json
from typer.testing import CliRunner
from hiking_router.cli import app


def test_generate_loop_emits_json_envelope():
    result = CliRunner().invoke(
        app,
        ["generate-loop", "--near", "Roanoke, VA", "--miles-min", "12", "--miles-max", "15", "--difficulty", "strenuous"],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert "query" in payload and "meta" in payload and "routes" in payload
    assert payload["routes"]
    ridge_fraction = payload["routes"][0]["terrain"]["ridge_fraction"]
    assert isinstance(ridge_fraction, (int, float))
    assert 0.0 <= float(ridge_fraction) <= 1.0
