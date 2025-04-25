"""User repository."""

from sqlmodel import select

from app.core.database import SessionDep, db_session

from .models import User


def create_user(user: User) -> None:
  """Create a user."""
  session: SessionDep = db_session.get()
  session.add(user)
  session.commit()


def get_user(username: str) -> User | None:
  """Get a user by email."""
  session: SessionDep = db_session.get()
  statement = select(User).where(User.email == username)
  result = session.exec(statement).first()
  return result
