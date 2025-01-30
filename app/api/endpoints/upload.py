"""
文件上传接口：处理画作图片的上传功能
包括：
1. 接收上传的图片文件
2. 验证文件格式和大小
3. 保存文件到指定目录
4. 返回上传状态和文件信息
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import enum
import shutil
import json
import hashlib
from pathlib import Path
from datetime import datetime

from app.core.database import get_db
from app.core.path_manager import PathManager
from app.models.painting_model import (
    Painting, PaintingCategory, 
    PaintingTechnique, InkColorStyle
)
from app.models.enums import InkColorStyle, PaintingCategory, PaintingTechnique

# 直接在这里定义枚举类
class InkColorStyle(str, enum.Enum):
    SHUIMO = "水墨"
    QINGLV = "青绿"
    QIANJIANG = "浅绛"
    SHESE = "设色"

class PaintingCategory(str, enum.Enum):
    PERSON = "人物"
    LANDSCAPE = "山水"
    FLOWER_BIRD = "花鸟"

class PaintingTechnique(str, enum.Enum):
    XIEYI = "写意"
    GONGBI = "工笔"
    BAIMIAO = "白描"
    MEIGU = "没骨"

router = APIRouter()
path_manager = PathManager(Path(__file__).resolve().parent.parent.parent.parent)

def parse_filename(filename: str) -> dict:
    """
    从文件名解析画作信息
    预期文件名格式：朝代_作者_标题_分类_技法_设色_尺寸_材质_收藏机构_标签.jpg
    例如：宋代_张择端_清明上河图_人物_工笔_设色_28.7cmX333.5cm_绢本_北京故宫博物院_人物,古装,彩绘.jpg
    """
    stem = Path(filename).stem
    parts = stem.split('_')
    
    info = {
        "dynasty": parts[0] if len(parts) > 0 else None,
        "author": parts[1] if len(parts) > 1 else None,
        "title": parts[2] if len(parts) > 2 else stem,
        "category": None,
        "technique": None,
        "ink_color_style": None,
        "dimension": None,
        "material": None,
        "museum": None,
        "tags": []
    }
    
    # 解析分类
    if len(parts) > 3:
        category_map = {
            "人物": PaintingCategory.PERSON,
            "山水": PaintingCategory.LANDSCAPE,
            "花鸟": PaintingCategory.FLOWER_BIRD
        }
        info["category"] = category_map.get(parts[3])
    
    # 解析技法
    if len(parts) > 4:
        technique_map = {
            "写意": PaintingTechnique.XIEYI,
            "工笔": PaintingTechnique.GONGBI,
            "白描": PaintingTechnique.BAIMIAO,
            "没骨": PaintingTechnique.MEIGU
        }
        info["technique"] = technique_map.get(parts[4])
    
    # 解析设色
    if len(parts) > 5:
        style_map = {
            "水墨": InkColorStyle.SHUIMO,
            "青绿": InkColorStyle.QINGLV,
            "浅绛": InkColorStyle.QIANJIANG,
            "设色": InkColorStyle.SHESE
        }
        info["ink_color_style"] = style_map.get(parts[5])
    
    # 解析尺寸
    if len(parts) > 6:
        info["dimension"] = parts[6]
    
    # 解析材质
    if len(parts) > 7:
        info["material"] = parts[7]
    
    # 解析收藏机构
    if len(parts) > 8:
        info["museum"] = parts[8]
    
    # 解析标签
    if len(parts) > 9:
        tag_str = parts[9]
        info["tags"] = tag_str.split(",") if tag_str else []
    
    return info

def update_json_metadata(
    existing_data: dict,
    new_data: dict,
    json_path: Path
) -> dict:
    """更新JSON元数据，保留已有信息"""
    # 合并数据，保留已有的非空值
    merged_data = existing_data.copy()
    for key, value in new_data.items():
        if value is not None and (key not in merged_data or merged_data[key] is None):
            merged_data[key] = value
            
    # 保存更新后的JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)
        
    return merged_data

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """接收文件并处理"""
    try:
        # 1. 先计算文件哈希
        contents = await file.read()
        file_hash = hashlib.md5(contents).hexdigest()
        
        # 2. 检查是否存在重复文件
        existing_painting = db.query(Painting).filter(
            Painting.file_hash == file_hash
        ).first()
        
        if existing_painting:
            return {
                "status": "skipped",
                "message": "文件已存在",
                "existing_id": existing_painting.id
            }
            
        # 3. 如果不存在重复，继续处理
        filename = file.filename
        file_location = path_manager.images_dir / filename
        
        with open(file_location, "wb") as buffer:
            buffer.write(contents)  # 使用已读取的内容
            
        # 4. 解析文件名
        info = parse_filename(filename)
            
        # 5. 创建数据库记录
        painting = Painting(
            title=info["title"],
            author=info["author"],
            dynasty=info["dynasty"],
            category=info["category"],
            technique=info["technique"],
            ink_color_style=info["ink_color_style"],
            file_path=str(file_location),
            file_hash=file_hash
        )
        db.add(painting)
        db.commit()
        db.refresh(painting)
        
        # 6. 检查是否存在JSON元数据
        json_path = path_manager.metadata_dir / f"{Path(filename).stem}.json"
        existing_data = {}
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        
        # 生成新的元数据
        new_data = {
            "id": painting.id,
            "file_hash": file_hash,
            "title": info["title"],
            "author": info["author"],
            "dynasty": info["dynasty"],
            "category": info["category"].value if info["category"] else None,
            "technique": info["technique"].value if info["technique"] else None,
            "ink_color_style": info["ink_color_style"].value if info["ink_color_style"] else None,
            "file_path": str(file_location),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # 更新JSON元数据
        final_data = update_json_metadata(existing_data, new_data, json_path)
        
        return {
            "filename": filename,
            "status": "uploaded",
            "metadata_path": str(json_path)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 