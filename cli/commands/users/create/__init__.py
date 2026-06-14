import typer
from cli.commands.users.create.employee import employee
from cli.commands.users.create.administrator import administrator

app = typer.Typer(help="Create users commands")

app.command()(employee)
app.command()(administrator)
