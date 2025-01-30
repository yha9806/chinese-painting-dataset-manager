"""
画作数据模型：定义画作在数据库中的存储结构
包括：
1. 基本信息（标题、作者、朝代等）
2. 分类信息（人物/山水/花鸟、写意/工笔、水墨/设色等）
3. 文件信息（存储路径、创建时间等）
4. 时间戳（创建时间、更新时间）
"""

import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
from app.core.database import Base

# ---------- 数据库枚举定义 ---------- #
class PaintingCategory(str, enum.Enum):
    """画作分类"""
    PERSON = "人物"
    LANDSCAPE = "山水"
    FLOWER_BIRD = "花鸟"

class PaintingTechnique(str, enum.Enum):
    """绘画技法"""
    XIEYI = "写意"
    GONGBI = "工笔"
    BAIMIAO = "白描"
    MEIGU = "没骨"

class InkColorStyle(str, enum.Enum):
    """墨色/设色风格"""
    SHUIMO = "水墨"
    QINGLV = "青绿"
    QIANJIANG = "浅绛"

class Painting(Base):
    """画作数据库模型"""
    __tablename__ = "paintings"

    id = Column(Integer, primary_key=True, index=True)
    file_hash = Column(String, unique=True, index=True)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=True, index=True)
    dynasty = Column(String, nullable=True)
    
    # 分类相关字段
    category = Column(Enum(PaintingCategory), nullable=True)
    technique = Column(Enum(PaintingTechnique), nullable=True)
    ink_color_style = Column(Enum(InkColorStyle), nullable=True)
    
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

"""
JSON Sidecar 模型：定义画作的详细元数据结构
包括：
1. 基本信息（ID、哈希值等）
2. 艺术信息（朝代、作者、标题等）
3. 分类信息（人物/山水/花鸟、写意/工笔、水墨/设色等）
4. 标签信息（自动/人工标注）
5. 注释信息（场景、技法等）
6. 历史背景（时代、作者生平等）
7. 参考文献
8. 审核状态
"""

from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field

class Tag(BaseModel):
    """标签模型"""
    tag_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: str = Field(default="auto", pattern="^(auto|manual|mixed)$")

class Reference(BaseModel):
    """参考文献模型"""
    type: str
    title: str
    author: str
    year: int
    link: Optional[str] = None

class ReviewStatus(BaseModel):
    """审核状态模型"""
    is_approved: bool = False
    reviewer: Optional[str] = None
    review_date: Optional[datetime] = None
    comments: Optional[str] = None

class Annotations(BaseModel):
    """注释信息模型"""
    scene_elements: List[str] = []
    technique_details: List[str] = []
    composition: Optional[str] = None

class HistoricalContext(BaseModel):
    """历史背景模型"""
    era_background: Optional[str] = None
    artist_biography: Optional[str] = None

class PaintingSidecar(BaseModel):
    """画作 Sidecar 主模型"""
    # 基本信息
    id: int
    file_hash: str
    
    # 艺术信息
    dynasty: Optional[str] = None
    author: Union[str, List[str]] = "佚名"
    title: str = "无题"
    artwork_form: Optional[str] = None
    material: Optional[str] = None
    dimensions: Optional[str] = None
    source_institution: Optional[str] = None
    
    # 分类信息（与数据库对应的枚举字段）
    category: Optional[PaintingCategory] = None
    technique: Optional[PaintingTechnique] = None
    ink_color_style: Optional[InkColorStyle] = None
    
    # 标签信息
    tags: List[Tag] = []
    
    # 创作信息
    date_of_creation: Optional[str] = None
    cultural_context: Optional[str] = None
    description: Optional[str] = None
    
    # 详细注释
    annotations: Optional[Annotations] = None
    
    # 历史背景
    historical_context: Optional[HistoricalContext] = None
    
    # 参考文献
    references: List[Reference] = []
    
    # 审核状态
    review_status: Optional[ReviewStatus] = None
    
    # 扩展字段
    ext_fields: Dict[str, Union[str, List[str], dict]] = {}

    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "file_hash": "abcdef1234567890abcdef1234567890",
                "dynasty": "清代",
                "author": "石涛",
                "title": "山水图",
                "artwork_form": "立轴",
                "material": "纸本",
                "dimensions": "180x96",
                "source_institution": "故宫博物院",
                "category": "山水",
                "technique": "写意",
                "ink_color_style": "水墨",
                "tags": [
                    {
                        "tag_name": "山水",
                        "confidence": 0.95,
                        "source": "auto"
                    }
                ],
                "date_of_creation": "康熙年间",
                "cultural_context": "文人画风盛行",
                "description": "此图展现了石涛独特的笔墨风格...",
                "ext_fields": {
                    "seals": ["闲章", "收藏印"],
                    "inscriptions": "淡墨题跋四行"
                }
            }
        } 