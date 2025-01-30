"""
路径管理模块：管理项目中所有重要的文件路径
包括：
1. 图片存储路径
2. 元数据存储路径
3. 临时文件路径
4. 自动创建必要的目录结构
"""

from pathlib import Path
import shutil
import logging
from typing import Optional, List
from datetime import datetime

class PathManager:
    """
    管理项目中可能用到的所有重要目录，如图像目录、元数据目录等。
    在初始化时自动创建这些目录（如果不存在）。
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.data_dir = base_dir / "data"

        # 定义各种目录
        self.images_dir = self.data_dir / "images"
        self.metadata_dir = self.data_dir / "metadata"
        self.processed_dir = self.data_dir / "processed"
        self.temp_dir = self.data_dir / "temp"
        self.logs_dir = base_dir / "logs"

        # 确保所有目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保所有必要的目录结构存在"""
        dirs = [
            self.images_dir,
            self.metadata_dir,
            self.processed_dir,
            self.temp_dir,
            self.logs_dir
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _init_directory_structure(self):
        """初始化完整的目录结构"""
        # 朝代目录
        dynasties = ["tang", "song", "yuan", "ming", "qing"]
        for dynasty in dynasties:
            (self.images_dir / "dynasty" / dynasty).mkdir(parents=True, exist_ok=True)
        
        # 风格目录
        styles = ["landscape", "figures", "flowers_birds", "freehand"]
        for style in styles:
            (self.images_dir / "style" / style).mkdir(parents=True, exist_ok=True)
        
        # 处理后的图片目录
        processed_types = ["thumbnails", "watermarked", "compressed"]
        for p_type in processed_types:
            (self.processed_dir / p_type).mkdir(parents=True, exist_ok=True)
        
        # 临时目录
        temp_types = ["uploads", "downloads"]
        for t_type in temp_types:
            (self.temp_dir / t_type).mkdir(parents=True, exist_ok=True)
        
        # 其他必要目录
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def get_image_path(self, dynasty: str, filename: str) -> Path:
        """获取按朝代分类的图片存储路径"""
        return self.images_dir / "dynasty" / dynasty / filename
    
    def get_style_path(self, style: str, filename: str) -> Path:
        """获取按风格分类的图片存储路径"""
        return self.images_dir / "style" / style / filename
    
    def get_temp_path(self, filename: str, type_: str = "uploads") -> Path:
        """获取临时文件路径"""
        return self.temp_dir / type_ / filename
    
    def clean_temp_files(self, max_age_hours: int = 24):
        """清理指定时间之前的临时文件"""
        now = datetime.now()
        for temp_type in ["uploads", "downloads"]:
            temp_path = self.temp_dir / temp_type
            for file_path in temp_path.glob("*"):
                if file_path.is_file():
                    file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if (now - file_age).total_seconds() > max_age_hours * 3600:
                        file_path.unlink()
                        logging.info(f"Cleaned temp file: {file_path}")
    
    def save_uploaded_file(self, temp_path: Path, dynasty: str, filename: str):
        """将上传的临时文件移动到正式存储位置"""
        dest_path = self.get_image_path(dynasty, filename)
        shutil.move(str(temp_path), str(dest_path))
        logging.info(f"Moved file from {temp_path} to {dest_path}")
        
        # 同时创建风格目录的软链接（如果需要）
        # style_path = self.get_style_path(style, filename)
        # if not style_path.exists():
        #     style_path.symlink_to(dest_path)
    
    def get_metadata_file_path(self, filename: str) -> Path:
        """获取元数据文件路径"""
        return self.metadata_dir / filename 