from typing import List, Optional
import json
import os
from datetime import datetime
from ..models.schemas import PaintingCreate, PaintingResponse

# 模拟数据库
paintings_db = []
next_id = 1

def get_all_paintings() -> List[PaintingResponse]:
    """获取所有画作"""
    return [PaintingResponse(**painting) for painting in paintings_db]

def create_painting(painting: PaintingCreate) -> PaintingResponse:
    """创建新画作"""
    global next_id
    painting_dict = painting.dict()
    painting_dict["id"] = next_id
    painting_dict["created_at"] = datetime.now()
    paintings_db.append(painting_dict)
    next_id += 1
    return PaintingResponse(**painting_dict)

def get_painting(painting_id: int) -> Optional[PaintingResponse]:
    """获取指定画作"""
    for painting in paintings_db:
        if painting["id"] == painting_id:
            return PaintingResponse(**painting)
    return None

def update_painting(painting_id: int, painting: PaintingCreate) -> Optional[PaintingResponse]:
    """更新画作信息"""
    for i, existing_painting in enumerate(paintings_db):
        if existing_painting["id"] == painting_id:
            # 保存旧文件路径
            old_image_path = existing_painting.get("image_path")
            old_json_path = existing_painting.get("json_path")
            
            # 更新画作信息
            painting_dict = painting.dict()
            painting_dict["id"] = painting_id
            painting_dict["created_at"] = existing_painting["created_at"]
            painting_dict["updated_at"] = datetime.now()
            
            # 删除旧文件
            if old_image_path and old_image_path != painting_dict.get("image_path"):
                try:
                    os.remove(old_image_path)
                except OSError:
                    pass
            
            if old_json_path and old_json_path != painting_dict.get("json_path"):
                try:
                    os.remove(old_json_path)
                except OSError:
                    pass
            
            paintings_db[i] = painting_dict
            return PaintingResponse(**painting_dict)
    return None

def delete_painting(painting_id: int) -> bool:
    """删除画作"""
    for i, painting in enumerate(paintings_db):
        if painting["id"] == painting_id:
            # 删除关联文件
            if painting.get("image_path"):
                try:
                    os.remove(painting["image_path"])
                except OSError:
                    pass
            
            if painting.get("json_path"):
                try:
                    os.remove(painting["json_path"])
                except OSError:
                    pass
            
            paintings_db.pop(i)
            return True
    return False 