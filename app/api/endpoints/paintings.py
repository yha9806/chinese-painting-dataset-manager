"""
画作管理接口：提供画作数据的增删改查功能
包括：
1. 获取画作列表（支持分页和多条件筛选）
2. 获取单个画作详情
3. 创建新画作记录
4. 更新画作信息
5. 删除画作记录
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import SessionLocal, get_db
from app.models.painting_model import Painting, PaintingCategory

router = APIRouter()

def get_db():
    """依赖项，获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def list_paintings(
    skip: int = 0,
    limit: int = 100,
    dynasty: Optional[str] = None,
    style: Optional[str] = None,
    author: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取画作列表，支持分页和多条件筛选"""
    query = db.query(Painting)
    
    if dynasty:
        query = query.filter(Painting.dynasty == dynasty)
    if style:
        query = query.filter(Painting.style == style)
    if author:
        query = query.filter(Painting.author == author)
    
    total = query.count()
    paintings = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "paintings": paintings,
        "page": skip // limit + 1,
        "total_pages": (total + limit - 1) // limit
    }

@router.get("/{painting_id}")
def get_painting(painting_id: int, db: Session = Depends(get_db)):
    """获取单个画作的详细信息"""
    painting = db.query(Painting).filter(Painting.id == painting_id).first()
    if not painting:
        raise HTTPException(status_code=404, detail="Painting not found")
    return painting

@router.post("/")
def create_painting(
    title: str,
    author: Optional[str] = None,
    dynasty: Optional[str] = None,
    style: Optional[str] = None,
    file_path: str = None,
    db: Session = Depends(get_db)
):
    """创建新的画作记录"""
    painting = Painting(
        title=title,
        author=author,
        dynasty=dynasty,
        style=style,
        file_path=file_path
    )
    db.add(painting)
    db.commit()
    db.refresh(painting)
    return painting

@router.put("/{painting_id}")
def update_painting(
    painting_id: int,
    title: Optional[str] = None,
    author: Optional[str] = None,
    dynasty: Optional[str] = None,
    style: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """更新画作信息"""
    painting = db.query(Painting).filter(Painting.id == painting_id).first()
    if not painting:
        raise HTTPException(status_code=404, detail="Painting not found")
    
    if title:
        painting.title = title
    if author:
        painting.author = author
    if dynasty:
        painting.dynasty = dynasty
    if style:
        painting.style = style
    
    painting.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(painting)
    return painting

@router.delete("/{painting_id}")
def delete_painting(painting_id: int, db: Session = Depends(get_db)):
    """删除画作记录"""
    painting = db.query(Painting).filter(Painting.id == painting_id).first()
    if not painting:
        raise HTTPException(status_code=404, detail="Painting not found")
    
    db.delete(painting)
    db.commit()
    return {"message": "Painting deleted successfully"}

@router.get("/search")
async def search_paintings(
    category: Optional[PaintingCategory] = None,
    dynasty: Optional[str] = None,
    author: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    按条件检索画作
    - category: 分类（人物/山水/花鸟）
    - dynasty: 朝代
    - author: 作者
    """
    query = db.query(Painting)
    
    if category:
        query = query.filter(Painting.category == category)
    if dynasty:
        query = query.filter(Painting.dynasty == dynasty)
    if author:
        query = query.filter(Painting.author == author)
        
    paintings = query.all()
    return {
        "total": len(paintings),
        "items": paintings
    } 