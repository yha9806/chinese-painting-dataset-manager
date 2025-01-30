"""
元数据管理接口：处理JSON Sidecar的查询和更新
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import json
from pathlib import Path

from app.core.database import get_db
from app.models.painting_model import Painting
from app.core.path_manager import PathManager
from app.core.log_utils import log_script_usage

log_script_usage(__file__)

router = APIRouter()
path_manager = PathManager(Path(__file__).resolve().parent.parent.parent.parent)

@router.get("/by-hash/{file_hash}")
async def get_metadata_by_hash(
    file_hash: str,
    db: Session = Depends(get_db)
):
    """根据文件哈希获取元数据"""
    painting = db.query(Painting).filter(
        Painting.file_hash == file_hash
    ).first()
    
    if not painting:
        raise HTTPException(status_code=404, detail="文件未找到")
        
    json_path = path_manager.metadata_dir / f"{Path(painting.file_path).stem}.json"
    if not json_path.exists():
        raise HTTPException(status_code=404, detail="元数据文件未找到")
        
    with open(json_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    return metadata

@router.get("/by-id/{painting_id}")
async def get_metadata_by_id(
    painting_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取元数据"""
    painting = db.query(Painting).filter(
        Painting.id == painting_id
    ).first()
    
    if not painting:
        raise HTTPException(status_code=404, detail="记录未找到")
        
    json_path = path_manager.metadata_dir / f"{Path(painting.file_path).stem}.json"
    if not json_path.exists():
        raise HTTPException(status_code=404, detail="元数据文件未找到")
        
    with open(json_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    return metadata 