import typer
import app.models.tables
from asyncio import run as aiorun
from app.services.role_service import RoleService
from app.repositories.role_repository import RoleRepository
from databases.postgresql import AsyncSessionLocal

app = typer.Typer()

async def create_role(name: str):
    async with AsyncSessionLocal() as db_session:
        repo = RoleRepository(db_session)
        service = RoleService(repo)
        await service.create_role(name)

@app.command()
def create(name: str):
    """
    Create a new role.

    This command creates a role with the specified name.

    The role name must be unique. If a role with the same name already
    exists, the creation is prevented.

    Args:
        name (str): The name of the role to create.

    Raises:
        conflict:
            If the role already exists.
        bad_request:
            If the role creation fails.

    Returns:
        None
    """
    aiorun(create_role(name=name))
    typer.echo(f"Adding roles {name}")

if __name__ == "__main__":
    app()
