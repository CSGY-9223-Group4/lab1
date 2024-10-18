import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock

from src.api.user_service import UserService
from src.api.note_service import NoteService
from src.app import create_app
from src.config import Settings
from src.db.database import Base

# Set up the test database
DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def engine():
    return create_engine(DATABASE_URL)


@pytest.fixture(scope="module")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="module")
def session(engine, tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def app():
    settings = Mock(spec=Settings)
    settings.JWT_SECRET_KEY = "test_secret_key"
    user_service = Mock(spec=UserService)
    note_service = Mock(spec=NoteService)
    app = create_app(user_service, note_service, settings)
    app.config["TESTING"] = True
    app.config["DEBUG"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()
