"""
数据库连接模块：负责创建和管理数据库连接
包括：
1. 创建数据库引擎（支持同步/异步）
2. 创建会话工厂
3. 定义基础模型类
4. 提供数据库会话依赖
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager, suppress
from typing import AsyncGenerator
import logging
import os
from pathlib import Path

from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

# 使用绝对路径
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = BASE_DIR / "sql_app.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 异步支持
# 创建异步引擎
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DB_ECHO,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """提供异步数据库会话"""
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error(f"Async database session error: {e}")
        with suppress(Exception):
            await session.rollback()
        raise
    finally:
        await session.close()

# 删除并重建数据库表
def init_db():
    print(f"正在重建数据库: {DB_FILE}")  # 打印路径以确认
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine) 