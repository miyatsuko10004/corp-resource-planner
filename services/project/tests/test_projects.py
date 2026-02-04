import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import Base
from datetime import date

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_project.db"
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
async def test_create_project_with_monthly_allocation(override_get_db):
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Create Project
        proj_payload = {
            "name": "AI Consulting",
            "contract_amount": 10000000,
            "start_date": "2026-04-01",
            "end_date": "2026-06-30",
            "customer_id": 1
        }
        resp_proj = await ac.post("/projects/", json=proj_payload)
        assert resp_proj.status_code == 201
        proj_id = resp_proj.json()["id"]

        # 2. Assign Member with Allocations
        assign_payload = {
            "employee_id": 1,
            "start_date": "2026-04-01",
            "end_date": "2026-06-30",
            "allocations": [
                {"month": "2026-04", "effort_percent": 50},
                {"month": "2026-05", "effort_percent": 100},
                {"month": "2026-06", "effort_percent": 80}
            ]
        }
        resp_assign = await ac.post(f"/projects/{proj_id}/assignments", json=assign_payload)
        assert resp_assign.status_code == 201
        
        data = resp_assign.json()
        assert len(data["allocations"]) == 3
        assert data["allocations"][1]["effort_percent"] == 100
