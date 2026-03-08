from typer.testing import CliRunner
from hiking_router.cli import app


def test_generate_loop_command_accepts_core_flags():
    result = CliRunner().invoke(
        app,
        [
            "generate-loop",
            "--near", "Roanoke, VA",
            "--miles-min", "12",
            "--miles-max", "15",
            "--difficulty", "strenuous",
        ],
    )
    assert result.exit_code == 0
    assert "Prototype loop near Roanoke, VA" in result.stdout
