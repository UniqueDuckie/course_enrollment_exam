import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.rate_limit import limiter


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _register(client, *, role, email, password="password123", name=None):
    name = name or role.capitalize()
    response = client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password, "role": role},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _login(client, email, password="password123"):
    response = client.post(
        "/auth/login", data={"username": email, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture()
def student_token(client):
    _register(client, role="student", email="student@x.com")
    return _login(client, "student@x.com")


@pytest.fixture()
def admin_token(client):
    _register(client, role="admin", email="admin@x.com")
    return _login(client, "admin@x.com")


@pytest.fixture()
def auth_header():
    def _build(token):
        return {"Authorization": f"Bearer {token}"}

    return _build
