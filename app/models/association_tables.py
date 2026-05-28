from sqlalchemy import Table, Column, ForeignKey
from databases.postgresql import Base

# Association table for many-to-many relationship between users and roles
role_user = Table(
    "role_user",
    Base.metadata,
    Column("role_id",ForeignKey("roles.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)
