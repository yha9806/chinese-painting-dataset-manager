from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..core.database import get_db
from ..models.paintings import Painting
from ..models.schemas import PaintingCreate, PaintingUpdate, PaintingResponse
from ..core.utils import (
    process_image, generate_filename, logger,
    save_json_data, load_json_data, delete_files, get_file_info
)
from ..services.deepseek_service import analyze_painting_info, validate_painting_data, search_related_info
import os
import json

router = APIRouter()

# 确保上传目录存在
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
    os.makedirs(os.path.join(UPLOAD_DIR, "images"))
    os.makedirs(os.path.join(UPLOAD_DIR, "json"))

@router.get("/paintings/", response_model=List[PaintingResponse])
async def get_paintings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    dynasty: Optional[str] = None,
    category: Optional[str] = None,
    artist: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取画作列表，支持分页和过滤"""
    query = db.query(Painting)
    
    if dynasty:
        query = query.filter(Painting.dynasty == dynasty)
    if category:
        query = query.filter(Painting.category == category)
    if artist:
        query = query.filter(Painting.artist == artist)
    
    paintings = query.offset(skip).limit(limit).all()
    return paintings

@router.get("/paintings/{painting_id}", response_model=PaintingResponse)
async def get_painting(painting_id: int, db: Session = Depends(get_db)):
    """获取单个画作详情"""
    painting = db.query(Painting).filter(Painting.id == painting_id).first()
    if painting is None:
        raise HTTPException(status_code=404, detail="画作未找到")
    return painting

@router.post("/paintings/", response_model=PaintingResponse)
async def create_painting(painting: PaintingCreate, db: Session = Depends(get_db)):
    """创建新画作"""
    try:
        db_painting = Painting(**painting.dict())
        db.add(db_painting)
        db.commit()
        db.refresh(db_painting)
        return db_painting
    except Exception as e:
        logger.error(f"创建画作时出错: {str(e)}")
        raise HTTPException(status_code=500, detail="创建画作失败")

@router.put("/paintings/{painting_id}", response_model=PaintingResponse)
async def update_painting(
    painting_id: int,
    painting: PaintingUpdate,
    db: Session = Depends(get_db)
):
    """更新画作信息"""
    db_painting = db.query(Painting).filter(Painting.id == painting_id).first()
    if db_painting is None:
        raise HTTPException(status_code=404, detail="画作未找到")
    
    try:
        update_data = painting.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_painting, key, value)
        
        db.commit()
        db.refresh(db_painting)
        return db_painting
    except Exception as e:
        logger.error(f"更新画作时出错: {str(e)}")
        raise HTTPException(status_code=500, detail="更新画作失败")

@router.delete("/paintings/{painting_id}")
async def delete_painting(painting_id: int, db: Session = Depends(get_db)):
    """删除画作"""
    db_painting = db.query(Painting).filter(Painting.id == painting_id).first()
    if db_painting is None:
        raise HTTPException(status_code=404, detail="画作未找到")
    
    try:
        # 删除关联的文件
        delete_files(db_painting.image_path, db_painting.json_path)
        
        db.delete(db_painting)
        db.commit()
        return {"message": "画作已成功删除"}
    except Exception as e:
        logger.error(f"删除画作时出错: {str(e)}")
        raise HTTPException(status_code=500, detail="删除画作失败")

@router.post("/paintings/{painting_id}/upload")
async def upload_files(
    painting_id: int,
    image: UploadFile = File(...),
    json_file: Optional[UploadFile] = File(None),
    metadata: Optional[str] = Form(None)
):
    """上传画作相关文件"""
    try:
        # 保存图片文件
        image_path = os.path.join(UPLOAD_DIR, "images", f"{painting_id}_{image.filename}")
        with open(image_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)

        # 处理JSON文件或metadata
        json_data = None
        json_path = None
        
        if json_file:
            json_path = os.path.join(UPLOAD_DIR, "json", f"{painting_id}_{json_file.filename}")
            content = await json_file.read()
            json_data = json.loads(content.decode())
            with open(json_path, "wb") as buffer:
                buffer.write(content)
        elif metadata:
            json_data = json.loads(metadata)
            json_path = os.path.join(UPLOAD_DIR, "json", f"{painting_id}_metadata.json")
            with open(json_path, "w", encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

        # 更新画作信息
        painting = get_painting(painting_id)
        if not painting:
            raise HTTPException(status_code=404, detail="画作不存在")

        painting_update = PaintingCreate(
            **painting.dict(),
            image_path=image_path,
            json_path=json_path,
            metadata=json_data
        )
        
        updated_painting = update_painting(painting_id, painting_update)
        return {"message": "文件上传成功", "painting": updated_painting}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的JSON格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.post("/upload-pair")
async def upload_file_pair(
    image: UploadFile = File(...),
    json_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传图片和JSON文件对"""
    try:
        # 验证文件类型
        if not image.filename.lower().endswith(('.jpg', '.jpeg')):
            raise HTTPException(status_code=400, detail="图片文件必须是JPG格式")
        if not json_file.filename.lower().endswith('.json'):
            raise HTTPException(status_code=400, detail="必须上传JSON文件")

        # 验证文件名匹配
        img_name = os.path.splitext(image.filename)[0]
        json_name = os.path.splitext(json_file.filename)[0]
        if img_name != json_name:
            raise HTTPException(status_code=400, detail="图片和JSON文件的文件名必须相同（除扩展名外）")

        # 创建目录（如果不存在）
        os.makedirs(os.path.join(UPLOAD_DIR, "images"), exist_ok=True)
        os.makedirs(os.path.join(UPLOAD_DIR, "json"), exist_ok=True)

        # 保存图片文件
        image_path = os.path.join(UPLOAD_DIR, "images", image.filename)
        with open(image_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)

        # 保存并解析JSON文件
        json_path = os.path.join(UPLOAD_DIR, "json", json_file.filename)
        json_content = await json_file.read()
        try:
            json_data = json.loads(json_content)
        except json.JSONDecodeError:
            if os.path.exists(image_path):
                os.remove(image_path)
            raise HTTPException(status_code=400, detail="无效的JSON格式")

        # 使用DeepSeek服务分析和补充信息
        enhanced_data = analyze_painting_info(image_path, json_data)
        
        # 验证数据准确性
        is_valid, message, validated_data = validate_painting_data(enhanced_data)
        if not is_valid:
            logger.warning(f"数据验证警告: {message}")
        
        # 搜索补充信息
        final_data = search_related_info(validated_data)
        
        # 保存更新后的JSON文件
        with open(json_path, "w", encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)

        # 创建画作记录
        painting_data = {
            "title": final_data.get("title", img_name),
            "artist": final_data.get("artist", "未知"),
            "dynasty": final_data.get("dynasty", "未知"),
            "category": final_data.get("category", "未知"),
            "description": final_data.get("description", ""),
            "painting_metadata": final_data,
            "image_path": image_path,
            "json_path": json_path
        }

        # 创建新的画作记录
        painting = PaintingCreate(**painting_data)
        db_painting = create_painting(painting)

        return {
            "message": "文件对上传成功，数据已完善",
            "validation_message": message if not is_valid else "数据验证通过",
            "painting": db_painting
        }

    except HTTPException:
        raise
    except Exception as e:
        # 清理任何已上传的文件
        for path in [image_path, json_path]:
            if 'path' in locals() and os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}") 