import typer
import cli.commands.users as users
import cli.commands.roles as roles
import app.core.logging

app = typer.Typer()
app.add_typer(roles.app, name="roles")
app.add_typer(users.app, name="users")


if __name__ == "__main__":
    app()