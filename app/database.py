from sqlmodel import create_engine, Session, SQLModel
from app.config import settings

connect_args = {}
if "neon.tech" in settings.DATABASE_URL:
    connect_args = {"sslmode": "require"}

engine = create_engine(
    settings.DATABASE_URL,
    echo=(settings.APP_ENV == "development"),
    pool_pre_ping=True,
    pool_size=5,           # Neon free tier has connection limits
    max_overflow=10,
    connect_args=connect_args,
)


def get_session():
    with Session(engine) as session:
        yield session


def init_db() -> None:
    from app.models import equipment, batch, unit_operation, dependency  # noqa: F401
    SQLModel.metadata.create_all(engine)