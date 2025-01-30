from fastapi.testclient import TestClient

def test_get_paintings(client):
    """测试获取画作列表"""
    response = client.get("/api/v1/paintings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_painting_by_id(client):
    """测试通过ID获取画作"""
    # 测试获取不存在的画作
    response = client.get("/api/v1/paintings/999")
    assert response.status_code == 404 