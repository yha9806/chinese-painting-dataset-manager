"""
配置模块：管理项目的所有配置信息
包括：
1. 基础配置（调试模式、时区等）
2. 服务器配置（主机、端口等）
3. 数据库配置（URL、连接池等）
4. 文件存储配置（目录、大小限制等）
5. 日志配置（级别、格式等）
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

# 确定项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # ---------- 基础配置 ---------- #
    # 环境配置
    ENV: str = os.getenv("ENV", "development")  # development, testing, production
    DEBUG: bool = ENV != "production"
    TIMEZONE: str = "Asia/Shanghai"
    
    # ---------- 服务器配置 ---------- #
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Chinese Painting Dataset"
    
    # ---------- 数据库配置 ---------- #
    # SQLite配置
    DB_DIR: Path = BASE_DIR / "data" / "database"
    DB_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_NAME: str = "paintings.db"
    DATABASE_URL: str = f"sqlite:///{DB_DIR}/{DATABASE_NAME}"
    
    # 数据库连接池配置
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    
    # 数据库配置
    ASYNC_DATABASE_URL: str = f"sqlite+aiosqlite:///{DB_DIR}/{DATABASE_NAME}"
    DB_ECHO: bool = False
    
    # ---------- 文件存储配置 ---------- #
    # 文件大小限制（单位：MB）
    MAX_UPLOAD_SIZE: int = 50
    
    # 允许的文件类型
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "gif"}
    
    # ---------- 日志配置 ---------- #
    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_DIR.mkdir(exist_ok=True)
    LOG_LEVEL: str = "INFO" if not DEBUG else "DEBUG"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # ---------- 安全配置 ---------- #
    # CORS配置
    ALLOW_ORIGINS: list = ["*"]
    ALLOW_METHODS: list = ["*"]
    ALLOW_HEADERS: list = ["*"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        
    def get_db_url(self) -> str:
        """根据环境返回数据库URL"""
        if self.ENV == "testing":
            return f"sqlite:///{self.DB_DIR}/test_{self.DATABASE_NAME}"
        return self.DATABASE_URL
    
    @property
    def is_development(self) -> bool:
        return self.ENV == "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENV == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.ENV == "testing"

@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()

# 导出配置实例
settings = get_settings()

# 确保日志目录存在
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

def validate_settings() -> None:
    """验证配置的有效性"""
    # 验证必要的目录是否存在且可写
    required_dirs = [
        settings.DB_DIR,
        settings.LOG_DIR
    ]
    
    for dir_path in required_dirs:
        if not dir_path.exists():
            sys.exit(f"错误：目录 {dir_path} 不存在")
        if not os.access(dir_path, os.W_OK):
            sys.exit(f"错误：目录 {dir_path} 不可写")
    
    # 验证数据库URL
    if not settings.DATABASE_URL:
        sys.exit("错误：未配置数据库URL")

# 在导入时验证配置
validate_settings() 