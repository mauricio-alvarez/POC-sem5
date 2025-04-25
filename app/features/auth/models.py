from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class UserRole(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", primary_key=True)
    role_id: Optional[int] = Field(default=None, foreign_key="roles.id", primary_key=True)

class User(SQLModel, table=True):
    __tablename__ = "users" # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    full_name: str = Field(unique=True, index=True, nullable=False)
    is_active: bool = Field(default=True)
    hashed_password: str = Field(nullable=False)
    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRole)


class Role(SQLModel, table=True):
    __tablename__ = "roles" # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(unique=True, index=True, nullable=False)
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)
