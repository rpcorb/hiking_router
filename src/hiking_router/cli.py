import typer
from hiking_router.models.query import LoopQuery
from hiking_router.use_cases.generate_loop import generate_top_loops

app = typer.Typer()


@app.callback()
def cli_root() -> None:
    """CLI root for hiking_router commands."""


@app.command("generate-loop")
def generate_loop(
    near: str = typer.Option(..., "--near"),
    miles_min: float = typer.Option(..., "--miles-min"),
    miles_max: float = typer.Option(..., "--miles-max"),
    difficulty: str = typer.Option(..., "--difficulty"),
) -> None:
    query = LoopQuery(
        near=near,
        miles_min=miles_min,
        miles_max=miles_max,
        difficulty=difficulty,
    )
    routes = generate_top_loops(query.model_dump())
    print(routes)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
