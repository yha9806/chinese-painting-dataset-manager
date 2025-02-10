import os
import json
import logging
from datetime import datetime
from PIL import Image
from pathlib import Path
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_directories():
    """创建必要的目录结构"""
    directories = ['data/images', 'data/jsons', 'logs']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def process_image(image_path: str, max_size: int = 1024):
    """处理上传的图片，调整大小和格式"""
    try:
        with Image.open(image_path) as img:
            # 转换为RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整图片大小
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 保存优化后的图片
            img.save(image_path, 'JPEG', quality=85, optimize=True)
            return True
    except Exception as e:
        logger.error(f"处理图片时出错: {str(e)}")
        return False

def save_json_data(data: Dict[str, Any], json_path: str) -> bool:
    """保存JSON数据到文件"""
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存JSON数据时出错: {str(e)}")
        return False

def load_json_data(json_path: str) -> Dict[str, Any]:
    """从文件加载JSON数据"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载JSON数据时出错: {str(e)}")
        return {}

def generate_filename(original_filename: str, file_type: str = 'image') -> str:
    """生成唯一的文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if file_type == 'image':
        extension = os.path.splitext(original_filename)[1]
        return f"{timestamp}{extension}"
    else:
        return f"{timestamp}.json"

def delete_files(*file_paths: str):
    """删除指定的文件"""
    for file_path in file_paths:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"删除文件时出错: {str(e)}")

def get_file_info(file_path: str) -> Dict[str, Any]:
    """获取文件信息"""
    try:
        stat = os.stat(file_path)
        return {
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime),
            "modified_at": datetime.fromtimestamp(stat.st_mtime),
            "path": file_path
        }
    except Exception as e:
        logger.error(f"获取文件信息时出错: {str(e)}")
        return {} 