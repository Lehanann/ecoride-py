import logging
from sqlalchemy.exc import IntegrityError
from app.core.exceptions.http_exceptions import conflict
from app.models.tables.role import Role
from app.repositories.role_repository import RoleRepository


logger = logging.getLogger(__name__)

class RoleService:
    """
    Service responsible for managing roles.

    This service provides methods to create individual roles and initialize
    default roles in the system.

    Note:
        Role management is restricted to internal usage via the CLI (GIIAR).
        These operations are not exposed through the public API.
    """
    ROLE_ALREADY_EXISTS = "Role already exists"

    def __init__(self, repository: RoleRepository):
        """
        Initialize the role service with the role repository.

        Args:
            repository (RoleRepository): The repository of the role.
        """
        self.repository = repository

    async def create_role(self, name: str) -> Role:
        """
        Create a new role.

        The role name is normalized (lowercased and trimmed) before creation.
        If the role already exists, an exception is raised.

        Args:
            name (str): Name of the role to create.

        Raises:
            conflict:
                If a role with the same name already exists.
            Exception:
                Re-raised for unexpected errors after rollback.

        Returns:
            Role: The newly created role instance.
        """
        name = name.lower().strip()
        role = await self.repository.get_by_name(name)

        if role:
            raise conflict(detail=self.ROLE_ALREADY_EXISTS)

        try:
            created_role = await self.repository.create(name=name)
            await self.repository.db.commit()
            return created_role
        except IntegrityError:
            await self.repository.db.rollback()
            logger.exception("Integrity error while creating role")
            raise conflict(detail=self.ROLE_ALREADY_EXISTS)
        except Exception:
            await self.repository.db.rollback()
            logger.exception("Unexpected error while creating role")
            raise

    async def init_default_roles(self, names: list[str]) -> None:
        """
        Initialize default roles.

        This method ensures that all provided role names exist in the database.
        Missing roles are created, while existing ones are ignored.

        This operation is idempotent and can be safely executed multiple times.

        Args:
            names (list[str]): List of role names to initialize.

        Raises:
            conflict:
                If a database integrity error occurs during creation.
            Exception:
                Re-raised for unexpected errors after rollback.
        """
        roles = await self.repository.get_all()
        existing_names = {role.name for role in roles}

        try:
            for name in names:
                normalized_name = name.lower().strip()
                if normalized_name not in existing_names:
                    await self.repository.create(name=normalized_name)
            await self.repository.db.commit()
        except IntegrityError:
            await self.repository.db.rollback()
            logger.exception("Integrity error while creating role")
            raise conflict(detail=self.ROLE_ALREADY_EXISTS)
        except Exception:
            await self.repository.db.rollback()
            logger.exception("Unexpected error while initializing roles")
            raise