import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import Base

# Test DB Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_resource.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(setup_db):
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def override_get_db(db_session):
    def _get_db():
        yield db_session
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_employee_with_skills(override_get_db):
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "name": "TDD Taro",
            "email": "taro@example.com",
            "role": "Consultant",
            "skills": ["Python", "FastAPI"],
            "unit_cost": 800000
        }
        response = await ac.post("/employees/", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "TDD Taro"
    assert len(data["skills"]) == 2
    assert data["skills"][0]["name"] in ["Python", "FastAPI"]

@pytest.mark.asyncio
async def test_search_employee_by_skill(override_get_db):
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create user with Python
        await ac.post("/employees/", json={
            "name": "Pythonista", "email": "py@example.com", "role": "Dev", 
            "skills": ["Python"], "unit_cost": 500000
        })
        # Create user with Java
        await ac.post("/employees/", json={
            "name": "Javanista", "email": "java@example.com", "role": "Dev", 
            "skills": ["Java"], "unit_cost": 500000
        })
        
        # Search for Python
        response = await ac.get("/employees/?skill=Python")
        
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Pythonista"
