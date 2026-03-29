import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from app.main import create_app
from app.database import get_session
from app.models import Equipment, Batch, UnitOperation, UnitOperationDependency  # noqa

TEST_DB_URL = "sqlite:///./test_bbp.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})


@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def session():
    with Session(test_engine) as s:
        yield s


@pytest.fixture
def client(session):
    app = create_app()

    def override():
        yield session

    app.dependency_overrides[get_session] = override
    return TestClient(app)