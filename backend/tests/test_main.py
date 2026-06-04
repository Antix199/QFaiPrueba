import os
import pytest
import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import Base, app, get_db

DATABASE_URL = "sqlite:///./qfai_test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./qfai_test.db"):
        os.remove("./qfai_test.db")

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_auth_flow():
    reg_data = {"username": "tester", "email": "tester@qfai.com", "password": "secretpassword"}
    res = client.post("/api/auth/register", json=reg_data)
    assert res.status_code == 201
    assert "token" in res.json()
    res_dup = client.post("/api/auth/register", json=reg_data)
    assert res_dup.status_code == 400
    login_data = {"email": "tester@qfai.com", "password": "secretpassword"}
    res_log = client.post("/api/auth/login", json=login_data)
    assert res_log.status_code == 200
    token = res_log.json()["token"]
    res_me = client.get(f"/api/auth/me?token={token}")
    assert res_me.status_code == 200
    assert res_me.json()["username"] == "tester"

def test_panorama_crud_and_join():
    login_data = {"email": "tester@qfai.com", "password": "secretpassword"}
    token = client.post("/api/auth/login", json=login_data).json()["token"]
    reg_data = {"username": "friend", "email": "friend@qfai.com", "password": "friendpassword"}
    friend_token = client.post("/api/auth/register", json=reg_data).json()["token"]
    future_date = (datetime.datetime.now() + datetime.timedelta(days=5)).isoformat()
    pan_data = {
        "title": "Partido de Fútbol en Temuco",
        "description": "Fútbol amigable 8v8 en la cancha sintética municipal.",
        "category": "Deporte",
        "date_time": future_date,
        "spots": 16,
        "location": "Temuco, Estadio German Becker",
        "latitude": -38.7408,
        "longitude": -72.6172
    }
    res_create = client.post(f"/api/panoramas?token={token}", json=pan_data)
    assert res_create.status_code == 201
    pan_id = res_create.json()["id"]
    res_list = client.get("/api/panoramas")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1
    res_join = client.post(f"/api/panoramas/{pan_id}/join?token={friend_token}")
    assert res_join.status_code == 200
    res_detail = client.get(f"/api/panoramas/{pan_id}?token={friend_token}")
    assert res_detail.status_code == 200
    assert res_detail.json()["participants_count"] == 1
    assert res_detail.json()["is_joined"] is True
    res_leave = client.post(f"/api/panoramas/{pan_id}/leave?token={friend_token}")
    assert res_leave.status_code == 200
    res_detail2 = client.get(f"/api/panoramas/{pan_id}")
    assert res_detail2.json()["participants_count"] == 0