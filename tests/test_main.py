from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.core.database import Base, get_db
import pytest
import os

# 使用测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    # 创建测试数据库表
    Base.metadata.create_all(bind=engine)
    yield
    # 清理测试数据库
    Base.metadata.drop_all(bind=engine)
    engine.dispose()  # 确保所有连接都被关闭
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except PermissionError:
            print("Warning: Could not remove test database file")

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "欢迎使用中国画数据集管理系统"}

def test_create_painting():
    painting_data = {
        "title": "测试画作",
        "artist": "测试艺术家",
        "dynasty": "测试朝代",
        "category": "测试类别",
        "description": "测试描述"
    }
    response = client.post("/api/paintings/", json=painting_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == painting_data["title"]
    assert data["artist"] == painting_data["artist"]
    assert "id" in data

def test_get_paintings():
    response = client.get("/api/paintings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_painting():
    # 先创建一个画作
    painting_data = {
        "title": "测试画作",
        "artist": "测试艺术家",
        "dynasty": "测试朝代",
        "category": "测试类别"
    }
    create_response = client.post("/api/paintings/", json=painting_data)
    painting_id = create_response.json()["id"]
    
    # 获取该画作
    response = client.get(f"/api/paintings/{painting_id}")
    assert response.status_code == 200
    assert response.json()["id"] == painting_id

def test_update_painting():
    # 先创建一个画作
    painting_data = {
        "title": "测试画作",
        "artist": "测试艺术家",
        "dynasty": "测试朝代",
        "category": "测试类别"
    }
    create_response = client.post("/api/paintings/", json=painting_data)
    painting_id = create_response.json()["id"]
    
    # 更新画作
    update_data = {
        "title": "更新后的画作",
        "artist": "更新后的艺术家",
        "dynasty": "更新后的朝代",
        "category": "更新后的类别"
    }
    response = client.put(f"/api/paintings/{painting_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == update_data["title"]

def test_delete_painting():
    # 先创建一个画作
    painting_data = {
        "title": "测试画作",
        "artist": "测试艺术家",
        "dynasty": "测试朝代",
        "category": "测试类别"
    }
    create_response = client.post("/api/paintings/", json=painting_data)
    painting_id = create_response.json()["id"]
    
    # 删除画作
    response = client.delete(f"/api/paintings/{painting_id}")
    assert response.status_code == 200
    
    # 确认画作已被删除
    get_response = client.get(f"/api/paintings/{painting_id}")
    assert get_response.status_code == 404

def test_analytics():
    # 测试统计接口
    endpoints = [
        "/api/analytics/dynasty",
        "/api/analytics/category",
        "/api/analytics/artist",
        "/api/analytics/timeline"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
        assert isinstance(response.json(), list) 