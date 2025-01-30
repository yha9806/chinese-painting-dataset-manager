"""
日志工具模块：提供统一的日志记录功能
包括：
1. 脚本使用记录
2. 错误日志记录
3. 操作日志记录
4. 自动创建日志目录
"""

import logging
from datetime import datetime
from pathlib import Path

def setup_logger():
    """设置全局日志配置"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def log_script_usage(script_path: str):
    """记录脚本使用情况"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 创建专门的脚本使用日志记录器
    script_logger = logging.getLogger('script_usage')
    if not script_logger.handlers:  # 避免重复添加处理程序
        script_logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_dir / "script_usage.log", encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        script_logger.addHandler(handler)
    
    script_logger.info(f"脚本使用: {script_path}")

def setup_logger(log_dir: Path):
    """设置日志配置"""
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    ) 