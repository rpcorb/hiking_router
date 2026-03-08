import typer

app = typer.Typer()


@app.command("generate-loop")
def generate_loop() -> None:
    print("Not implemented")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
