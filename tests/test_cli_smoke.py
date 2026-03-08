from typer.testing import CliRunner
from hiking_router.cli import app


def test_cli_shows_help():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "generate-loop" in result.stdout
