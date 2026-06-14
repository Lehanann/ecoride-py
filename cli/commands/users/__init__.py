import typer
import cli.commands.users.create as create

app = typer.Typer(help="Internals users management commands")

app.add_typer(create.app, name="create")