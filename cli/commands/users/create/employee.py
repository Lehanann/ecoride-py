from typing import Annotated
import typer
import app.models.tables
from asyncio import run as aiorun
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.core.exceptions.data_exceptions import DataIntegrityError
from databases.postgresql import AsyncSessionLocal
from app.schemas.user_schema import UserCreate

app = typer.Typer()

DOMAIN = "exemple.fr"

async def create_employee_user(user: UserCreate):
    async with AsyncSessionLocal() as db:
        user_repository = UserRepository(db)
        role_repository = RoleRepository(db)
        service = UserService(user_repository, role_repository)
        await service.create_employee_user(user)

@app.command()
def employee(
        firstname: Annotated[str, typer.Argument(help="First name of the employee")],
        lastname: Annotated[str, typer.Argument(help="Last name of the employee")],
):
    """
    Create a new employee account.

    This command creates a user with the employee role.
    It requires the employee's first and last name, and automatically
    generates a username and email using the configured domain.

    Additional information such as phone number, address, and birth date
    can be provided optionally. These fields can be skipped by pressing ENTER.

    The command prompts for a password and confirmation.

    Args:
        firstname (str): First name of the employee.
        lastname (str): Last name of the employee.

    Raises:
        conflict:
            If a user with the same email already exists.
        bad_request:
            If the passwords do not match or input is invalid.
        not_found:
            If the employee role cannot be found.
        DataIntegrityError:
            If a critical data inconsistency is detected.

    Returns:
        None
    """
    password: str = typer.prompt("Enter your password")
    confirm_password: str = typer.prompt("Confirm your password")

    phone = typer.prompt("Enter your phone number (optional)", default="")
    address = typer.prompt("Enter your address (optional)", default="")
    birth_date = typer.prompt("Enter your birth date (YYYY-MM-DD) (optional)", default="")


    username = firstname[0].lower().strip() + lastname.lower().strip()
    email = username + "@" + DOMAIN


    user_data = {
        "username": username,
        "email": email,
        "firstname": firstname,
        "lastname": lastname,
        "password": password,
        "confirm_password": confirm_password,
        "phone": phone or None,
        "address": address or None,
        "birth_date": birth_date or None,
    }
    try:
        user = UserCreate(**user_data)
        aiorun(create_employee_user(user))
        typer.secho("✅ User created successfully.", fg="green")
    except DataIntegrityError as e:
        typer.secho(f"❌ Critical system error. Check logs.", fg="red")
    except Exception as e:
        typer.secho(f"❌ Error: {e}", fg="red")
