import typer
from cli.commands.roles.init import init
from cli.commands.roles.create import create

app = typer.Typer(help="Role management commands")

app.command()(create)
app.command()(init)
