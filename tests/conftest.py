import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.core.db import Base, get_db

# ========================
# Setup test database
# ========================
if os.getenv("GITHUB_ACTIONS") == "true":
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    connect_args = {"check_same_thread": False}
else:
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/rover_backend_test"
    connect_args = {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Drop & create tables baru untuk testing
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# ========================
# Dependency override
# ========================
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ========================
# Pytest fixture TestClient
# ========================
@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client
