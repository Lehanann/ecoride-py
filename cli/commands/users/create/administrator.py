from typing import Annotated

import typer
import app.models.tables
from asyncio import run as aiorun
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from databases.postgresql import AsyncSessionLocal
from app.schemas.user_schema import UserCreate

app = typer.Typer()

async def create_admin_user(user: UserCreate):
    async with AsyncSessionLocal() as db:
        user_repository = UserRepository(db)
        role_repository = RoleRepository(db)
        service = UserService(user_repository, role_repository)
        await service.create_admin_user(user)

@app.command()
def administrator(
        username: Annotated[str, typer.Option(prompt=True, help="Administrator account")],
        email: Annotated[str, typer.Option(prompt=True, help="Administrator email")],
        password: Annotated[str, typer.Option(prompt=True, help="Password")],
        confirm_password: Annotated[str, typer.Option(prompt=True)]
    ):
    """
    Create the administrator account.

    This command creates a unique administrator user.
    If an administrator already exists, the creation is prevented.

    The email is automatically generated using the configured domain.

    The command prompts for a password and confirmation.

    Raises:
        conflict:
            If an administrator already exists.
        bad_request:
            If the passwords do not match.
        DataIntegrityError:
            If multiple administrators are detected in the system.

    Returns:
        None
    """

    user_data = {
        "username": username,
        "email": email,
        "password": password,
        "confirm_password": confirm_password
    }
    user = UserCreate(**user_data)
    aiorun(create_admin_user(user))