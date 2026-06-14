import typer
import app.models.tables
from asyncio import run as aiorun
from app.services.role_service import RoleService
from app.repositories.role_repository import RoleRepository
from databases.postgresql import AsyncSessionLocal

app = typer.Typer()

async def init_roles(roles:list[str]):
    async with AsyncSessionLocal() as db_session:
        repo = RoleRepository(db_session)
        service = RoleService(repo)
        await service.init_default_roles(roles)


@app.command()
def init():
    """
    Initialize default roles.

    This command creates the default roles required by the application
    (e.g. administrator, employee).

    It is typically used during the initial setup of the system.

    If roles already exist, they may be skipped or raise a conflict
    depending on implementation.

    Raises:
        conflict:
            If a role already exists (depending on implementation).
        bad_request:
            If an error occurs during initialization.

    Returns:
        None
    """
    ROLES_DEFAULT = ["passenger", "driver", "employee", "administrator"]
    aiorun(init_roles(roles=ROLES_DEFAULT))
    typer.echo("Initialization default roles")

async def create_role(name: str):
    async with AsyncSessionLocal() as db_session:
        repo = RoleRepository(db_session)
        service = RoleService(repo)
        await service.create_role(name)