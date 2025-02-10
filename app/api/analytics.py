from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from ..core.database import get_db
from ..models.paintings import Painting

router = APIRouter()

@router.get("/analytics/dynasty")
async def get_dynasty_stats(db: Session = Depends(get_db)):
    """获取各朝代画作数量统计"""
    stats = db.query(
        Painting.dynasty,
        func.count(Painting.id).label('count')
    ).group_by(Painting.dynasty).all()
    
    return [{"dynasty": item[0], "count": item[1]} for item in stats]

@router.get("/analytics/category")
async def get_category_stats(db: Session = Depends(get_db)):
    """获取各类别画作数量统计"""
    stats = db.query(
        Painting.category,
        func.count(Painting.id).label('count')
    ).group_by(Painting.category).all()
    
    return [{"category": item[0], "count": item[1]} for item in stats]

@router.get("/analytics/artist")
async def get_artist_stats(db: Session = Depends(get_db)):
    """获取艺术家作品数量统计"""
    stats = db.query(
        Painting.artist,
        func.count(Painting.id).label('count')
    ).group_by(Painting.artist).all()
    
    return [{"artist": item[0], "count": item[1]} for item in stats]

@router.get("/analytics/timeline")
async def get_timeline_stats(db: Session = Depends(get_db)):
    """获取画作创建时间统计"""
    stats = db.query(
        func.date(Painting.created_at),
        func.count(Painting.id).label('count')
    ).group_by(func.date(Painting.created_at)).all()
    
    return [{"date": str(item[0]), "count": item[1]} for item in stats] 