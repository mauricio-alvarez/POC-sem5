from sqlite3 import connect
from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings

# settings = get_settings()

connect_args = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)

async def get_session():
  """Get the database session.

  Returns:
    session: The database session.
  """
  with Session(engine) as session:
    token = db_session.set(session)
    yield session
    db_session.reset(token)


SessionDep = Annotated[Session, Depends(get_session)]

db_session: ContextVar[Session] = ContextVar("db_session")

