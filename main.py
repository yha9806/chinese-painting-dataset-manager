"""
Chinese Painting Dataset Management System
基于 FastAPI + SQLite + SQLAlchemy 的中国画数据集管理系统
"""

import sys
import logging
import uvicorn
import webbrowser
from threading import Timer
from pathlib import Path

# 确保当前目录在 Python 路径中
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# 记录脚本使用
from app.core.log_utils import log_script_usage, setup_logger
setup_logger()  # 设置全局日志配置
log_script_usage(__file__)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine, init_db
from app.core.path_manager import PathManager
from app.api.endpoints import upload, download, paintings, author_stats

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(BASE_DIR / "logs" / "app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# 在文件顶部，其他导入后添加
path_manager = PathManager(BASE_DIR)

def create_app():
    # 初始化数据库
    init_db()
    logging.info("Database tables reinitialized.")
    
    # 初始化路径管理器（删除这行，因为已经在全局定义）
    logging.info("Directory structure initialized.")
    
    # 初始化 FastAPI 应用
    app = FastAPI(
        title="Chinese Painting Dataset Management System",
        description="中国画数据集管理系统API",
        version="1.0.0"
    )
    
    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(upload.router, prefix="/api/v1/upload", tags=["上传管理"])
    app.include_router(download.router, prefix="/api/v1/download", tags=["下载管理"])
    app.include_router(paintings.router, prefix="/api/v1/paintings", tags=["画作管理"])
    app.include_router(author_stats.router, prefix="/api/v1", tags=["作者和统计管理"])
    
    return app

# 创建应用实例
app = create_app()

@app.get("/", tags=["系统信息"])
async def root():
    """系统根路径信息"""
    return {
        "system": "Chinese Painting Dataset Management System",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs"
    }

@app.get("/health", tags=["系统信息"])
async def health_check():
    """系统健康检查"""
    try:
        # 检查必要目录是否存在
        required_dirs = [
            path_manager.images_dir,
            path_manager.metadata_dir,
            path_manager.processed_dir,
            path_manager.temp_dir
        ]
        
        status = {str(d): d.exists() for d in required_dirs}
        
        return {
            "status": "healthy",
            "directory_check": status,
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def open_browser():
    """自动打开浏览器到文档页面"""
    webbrowser.open(f"http://{settings.HOST}:{settings.PORT}/docs")

if __name__ == "__main__":
    # 延迟1.5秒后自动打开浏览器
    Timer(1.5, open_browser).start()
    logging.info(f"Starting server at http://{settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
