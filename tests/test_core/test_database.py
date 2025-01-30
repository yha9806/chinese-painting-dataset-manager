import pytest
from sqlalchemy.orm import Session
from app.core.database import get_db

def test_get_db(db_session):
    """测试数据库会话创建"""
    assert isinstance(db_session, Session)
    
def test_database_connection(db_session):
    """测试数据库连接"""
    result = db_session.execute("SELECT 1").scalar()
    assert result == 1 