import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client():
    """同步 TestClient，使用应用 lifespan 自动初始化数据库"""
    with TestClient(app) as c:
        yield c


