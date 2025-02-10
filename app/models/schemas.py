from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class PaintingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="画作标题", example="富春山居图")
    artist: str = Field(..., min_length=1, max_length=100, description="艺术家姓名", example="黄公望")
    dynasty: str = Field(..., min_length=1, max_length=50, description="朝代", example="元朝")
    category: str = Field(..., min_length=1, max_length=50, description="画作类别", example="山水画")
    description: Optional[str] = Field(None, max_length=1000, description="画作描述", example="中国十大传世名画之一")
    image_path: Optional[str] = None
    json_path: Optional[str] = None
    painting_metadata: Optional[Dict[str, Any]] = Field(None, description="画作的额外元数据", example={
        "size": "纵25.5厘米，横636.9厘米",
        "material": "纸本水墨",
        "collection": "浙江省博物馆",
        "creation_date": "约1350年",
        "technique": ["水墨", "勾勒", "皴法"],
        "preservation_state": "良好",
        "historical_significance": "重要"
    })

class PaintingCreate(PaintingBase):
    class Config:
        json_schema_extra = {
            "example": {
                "title": "富春山居图",
                "artist": "黄公望",
                "dynasty": "元朝",
                "category": "山水画",
                "description": "中国十大传世名画之一",
                "painting_metadata": {
                    "size": "纵25.5厘米，横636.9厘米",
                    "material": "纸本水墨",
                    "collection": "浙江省博物馆"
                }
            }
        }

class PaintingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, example="富春山居图")
    artist: Optional[str] = Field(None, min_length=1, max_length=100, example="黄公望")
    dynasty: Optional[str] = Field(None, min_length=1, max_length=50, example="元朝")
    category: Optional[str] = Field(None, min_length=1, max_length=50, example="山水画")
    description: Optional[str] = Field(None, max_length=1000, example="中国十大传世名画之一")
    painting_metadata: Optional[Dict[str, Any]] = Field(None, description="画作的额外元数据")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "富春山居图",
                "artist": "黄公望",
                "dynasty": "元朝",
                "category": "山水画",
                "description": "中国十大传世名画之一",
                "painting_metadata": {
                    "size": "纵25.5厘米，横636.9厘米",
                    "material": "纸本水墨"
                }
            }
        }

class PaintingInDB(PaintingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaintingResponse(PaintingInDB):
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "富春山居图",
                "artist": "黄公望",
                "dynasty": "元朝",
                "category": "山水画",
                "description": "中国十大传世名画之一",
                "painting_metadata": {
                    "size": "纵25.5厘米，横636.9厘米",
                    "material": "纸本水墨",
                    "collection": "浙江省博物馆"
                },
                "image_path": "data/images/20250210_123456.jpg",
                "json_path": "data/jsons/20250210_123456.json",
                "created_at": "2025-02-10T12:34:56",
                "updated_at": "2025-02-10T12:34:56"
            }
        } 