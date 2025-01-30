"""
作者和统计信息接口：提供作者管理和数据统计功能
包括：
1. 作者管理（列表、作品查询等）
2. 作者统计（作品数量、风格分布等）
3. 整体统计（画作总量、存储信息等）
4. 时间统计（每日上传量等）
5. 分类统计（题材、技法、设色分布等）
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path

from app.core.database import SessionLocal
from app.models.painting_model import (
    Painting, PaintingCategory, 
    PaintingTechnique, InkColorStyle
)
from app.core.path_manager import PathManager

router = APIRouter()
path_manager = PathManager(Path(__file__).resolve().parent.parent.parent.parent)

def get_db():
    """依赖项，获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- 作者管理接口 -------- #
@router.get("/authors")
def list_authors(dynasty: Optional[str] = None, db: Session = Depends(get_db)):
    """获取作者列表，可按朝代筛选"""
    query = db.query(Painting.author).distinct()
    if dynasty:
        query = query.filter(Painting.dynasty == dynasty)
    authors = query.all()
    return {"authors": [author[0] for author in authors if author[0]]}

@router.get("/authors/{author_name}/works")
def get_author_works(author_name: str, db: Session = Depends(get_db)):
    """获取指定作者的所有作品"""
    paintings = db.query(Painting)\
        .filter(Painting.author == author_name)\
        .all()
    if not paintings:
        raise HTTPException(status_code=404, detail=f"未找到作者: {author_name}")
    return {
        "author": author_name,
        "total_works": len(paintings),
        "works": paintings
    }

# -------- 统计信息接口 -------- #
@router.get("/statistics/summary")
def get_statistics(db: Session = Depends(get_db)):
    """返回总体统计信息"""
    try:
        # 数据库统计
        painting_count = db.query(Painting).count()
        dynasty_stats = db.query(Painting.dynasty, func.count(Painting.id))\
            .group_by(Painting.dynasty).all()
        style_stats = db.query(Painting.style, func.count(Painting.id))\
            .group_by(Painting.style).all()
        
        # 文件系统统计
        image_files = list(path_manager.images_dir.glob("**/*.jpg"))
        total_size = sum(f.stat().st_size for f in image_files) / (1024 * 1024)
        
        return {
            "total_paintings": painting_count,
            "dynasty_distribution": dict(dynasty_stats),
            "style_distribution": dict(style_stats),
            "storage": {
                "total_files": len(image_files),
                "total_size_mb": round(total_size, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/daily")
def get_daily_stats(db: Session = Depends(get_db)):
    """返回每日上传统计"""
    try:
        daily_stats = db.query(
            func.date(Painting.created_at),
            func.count(Painting.id)
        ).group_by(
            func.date(Painting.created_at)
        ).all()
        
        return {
            "daily_uploads": dict(daily_stats)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------- 分类统计接口 -------- #
@router.get("/statistics/categories")
def get_category_stats(db: Session = Depends(get_db)):
    """获取画作分类统计信息"""
    try:
        # 题材分布
        category_stats = db.query(
            Painting.category, 
            func.count(Painting.id).label('count')
        ).group_by(Painting.category).all()
        
        # 技法分布
        technique_stats = db.query(
            Painting.technique, 
            func.count(Painting.id).label('count')
        ).group_by(Painting.technique).all()
        
        # 设色分布
        ink_color_stats = db.query(
            Painting.ink_color_style, 
            func.count(Painting.id).label('count')
        ).group_by(Painting.ink_color_style).all()
        
        # 朝代分布（按数量降序）
        dynasty_stats = db.query(
            Painting.dynasty,
            func.count(Painting.id).label('count')
        ).group_by(Painting.dynasty)\
         .order_by(desc('count')).all()
        
        # 计算百分比
        total_paintings = db.query(func.count(Painting.id)).scalar()
        
        return {
            "total_paintings": total_paintings,
            "category_distribution": {
                str(cat.value if cat else "未知"): {
                    "count": count,
                    "percentage": round(count / total_paintings * 100, 2)
                }
                for cat, count in category_stats
            },
            "technique_distribution": {
                str(tech.value if tech else "未知"): {
                    "count": count,
                    "percentage": round(count / total_paintings * 100, 2)
                }
                for tech, count in technique_stats
            },
            "ink_color_distribution": {
                str(style.value if style else "未知"): {
                    "count": count,
                    "percentage": round(count / total_paintings * 100, 2)
                }
                for style, count in ink_color_stats
            },
            "dynasty_distribution": {
                str(dynasty if dynasty else "未知"): {
                    "count": count,
                    "percentage": round(count / total_paintings * 100, 2)
                }
                for dynasty, count in dynasty_stats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/trends")
def get_trend_stats(
    db: Session = Depends(get_db),
    period: str = "monthly"  # monthly 或 yearly
):
    """获取画作上传趋势统计"""
    try:
        if period == "monthly":
            # 按月统计
            trend_stats = db.query(
                func.strftime('%Y-%m', Painting.created_at).label('month'),
                func.count(Painting.id).label('count'),
                func.count(case([(Painting.category == PaintingCategory.LANDSCAPE, 1)])).label('landscape_count'),
                func.count(case([(Painting.category == PaintingCategory.PERSON, 1)])).label('person_count'),
                func.count(case([(Painting.category == PaintingCategory.FLOWER_BIRD, 1)])).label('flower_bird_count')
            ).group_by('month')\
             .order_by('month').all()
            
            return {
                "period": "monthly",
                "trends": [
                    {
                        "date": month,
                        "total": count,
                        "categories": {
                            "山水": landscape_count,
                            "人物": person_count,
                            "花鸟": flower_bird_count
                        }
                    }
                    for month, count, landscape_count, person_count, flower_bird_count 
                    in trend_stats
                ]
            }
        else:
            # 按年统计
            trend_stats = db.query(
                func.strftime('%Y', Painting.created_at).label('year'),
                func.count(Painting.id).label('count')
            ).group_by('year')\
             .order_by('year').all()
            
            return {
                "period": "yearly",
                "trends": [
                    {
                        "year": year,
                        "count": count
                    }
                    for year, count in trend_stats
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/correlations")
def get_correlation_stats(db: Session = Depends(get_db)):
    """获取画作特征相关性统计"""
    try:
        # 技法与设色的关联统计
        technique_color_stats = db.query(
            Painting.technique,
            Painting.ink_color_style,
            func.count(Painting.id).label('count')
        ).group_by(
            Painting.technique,
            Painting.ink_color_style
        ).all()
        
        # 朝代与分类的关联统计
        dynasty_category_stats = db.query(
            Painting.dynasty,
            Painting.category,
            func.count(Painting.id).label('count')
        ).group_by(
            Painting.dynasty,
            Painting.category
        ).all()
        
        return {
            "technique_color_correlation": {
                f"{tech.value if tech else '未知'}__{color.value if color else '未知'}": count
                for tech, color, count in technique_color_stats
            },
            "dynasty_category_correlation": {
                f"{dynasty if dynasty else '未知'}__{cat.value if cat else '未知'}": count
                for dynasty, cat, count in dynasty_category_stats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/author_analysis")
def get_author_analysis(db: Session = Depends(get_db)):
    """作者相关分析统计"""
    try:
        # 作者作品数量分布
        author_work_counts = db.query(
            Painting.author,
            func.count(Painting.id).label('work_count')
        ).group_by(Painting.author)\
         .order_by(desc('work_count'))\
         .limit(10).all()
        
        # 作者偏好分析
        author_preferences = db.query(
            Painting.author,
            Painting.category,
            func.count(Painting.id).label('count')
        ).filter(Painting.author.isnot(None))\
         .group_by(Painting.author, Painting.category)\
         .having(func.count(Painting.id) > 5)\
         .order_by(desc('count')).all()
        
        return {
            "top_authors": [
                {
                    "author": author if author else "佚名",
                    "work_count": count,
                }
                for author, count in author_work_counts
            ],
            "author_preferences": [
                {
                    "author": author if author else "佚名",
                    "category": cat.value if cat else "未知",
                    "count": count
                }
                for author, cat, count in author_preferences
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/time_analysis")
def get_time_analysis(db: Session = Depends(get_db)):
    """时间维度分析"""
    try:
        # 每日上传高峰期分析
        hourly_stats = db.query(
            func.strftime('%H', Painting.created_at).label('hour'),
            func.count(Painting.id).label('count')
        ).group_by('hour')\
         .order_by('hour').all()
        
        # 季节性分析
        seasonal_stats = db.query(
            func.strftime('%m', Painting.created_at).label('month'),
            func.count(Painting.id).label('count')
        ).group_by('month')\
         .order_by('month').all()
        
        return {
            "hourly_distribution": [
                {
                    "hour": int(hour),
                    "count": count
                }
                for hour, count in hourly_stats
            ],
            "seasonal_distribution": [
                {
                    "month": int(month),
                    "count": count
                }
                for month, count in seasonal_stats
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/quality_metrics")
def get_quality_metrics(db: Session = Depends(get_db)):
    """画作质量相关指标统计"""
    try:
        # 技法完整度统计
        technique_completion = db.query(
            func.count(case([(Painting.technique.isnot(None), 1)])) * 100.0 / 
            func.count(Painting.id)
        ).scalar()
        
        # 分类完整度统计
        category_completion = db.query(
            func.count(case([(Painting.category.isnot(None), 1)])) * 100.0 / 
            func.count(Painting.id)
        ).scalar()
        
        # 设色完整度统计
        color_completion = db.query(
            func.count(case([(Painting.ink_color_style.isnot(None), 1)])) * 100.0 / 
            func.count(Painting.id)
        ).scalar()
        
        return {
            "metadata_completion": {
                "technique": round(technique_completion, 2),
                "category": round(category_completion, 2),
                "ink_color": round(color_completion, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 