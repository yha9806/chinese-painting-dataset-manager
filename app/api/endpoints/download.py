from app.core.log_utils import log_script_usage
log_script_usage(__file__)

"""
文件下载接口：处理画作图片的下载功能
包括：
1. 单个文件下载
2. 批量文件打包下载
3. 支持自定义文件名
4. 支持流式响应
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional
import zipfile
import io
from pathlib import Path
from app.core.path_manager import PathManager
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.painting_model import Painting, PaintingCategory
import tempfile  # 添加 tempfile

router = APIRouter()
path_manager = PathManager(Path(__file__).resolve().parent.parent.parent.parent)

# 添加安全路径检查工具函数
def verify_safe_path(file_path: Path, base_dir: Path) -> bool:
    """验证文件路径是否在安全目录内"""
    try:
        return base_dir in file_path.resolve().parents
    except (ValueError, RuntimeError):
        return False

# 添加画作查询工具函数
def get_filtered_paintings(
    db: Session,
    category: Optional[PaintingCategory] = None,
    dynasty: Optional[str] = None,
    author: Optional[str] = None
) -> List[Painting]:
    """根据条件筛选画作"""
    query = db.query(Painting)
    if category:
        query = query.filter(Painting.category == category)
    if dynasty:
        query = query.filter(Painting.dynasty == dynasty)
    if author:
        query = query.filter(Painting.author == author)
    return query.all()

# 修改单文件下载路由
@router.get("/single/{filename}")
async def download_single_file(
    filename: str,
    db: Session = Depends(get_db)
):
    """下载单个画作文件"""
    painting = db.query(Painting).filter(Painting.file_path.endswith(filename)).first()
    if not painting:
        raise HTTPException(status_code=404, detail="文件未找到")
        
    file_path = Path(painting.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
        
    # 安全路径检查
    if not verify_safe_path(file_path, path_manager.images_dir):
        raise HTTPException(status_code=400, detail="非法文件路径")
        
    return FileResponse(
        file_path,
        filename=filename
    )

# 修改批量下载路由
@router.get("/batch")
async def batch_download(
    category: Optional[PaintingCategory] = Query(None),
    dynasty: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """批量下载符合条件的画作"""
    paintings = get_filtered_paintings(db, category, dynasty, author)
    
    if not paintings:
        raise HTTPException(status_code=404, detail="未找到符合条件的画作")
    
    # 使用内存流而不是临时文件
    zip_stream = io.BytesIO()
    with zipfile.ZipFile(zip_stream, "w", zipfile.ZIP_DEFLATED) as zf:
        for painting in paintings:
            file_path = Path(painting.file_path)
            if not file_path.exists():
                continue
            if not verify_safe_path(file_path, path_manager.images_dir):
                continue
            zf.write(file_path, file_path.name)
    
    zip_stream.seek(0)
    return StreamingResponse(
        zip_stream,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename=paintings_{category.value if category else "all"}.zip'
        }
    )

@router.post("/batch")
def batch_download_files(filenames: List[str]):
    """批量文件打包下载"""
    zip_stream = io.BytesIO()
    
    with zipfile.ZipFile(zip_stream, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename in filenames:
            file_path = path_manager.images_dir / filename
            if not file_path.exists():
                continue
            
            with open(file_path, 'rb') as f:
                zf.writestr(filename, f.read())
    
    zip_stream.seek(0)
    
    return StreamingResponse(
        zip_stream,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment;filename=paintings.zip"}
    )

# 下载指定分类的画作
@router.get("/batch")
async def batch_download_category(
    category: Optional[PaintingCategory] = None,
    db: Session = Depends(get_db)
):
    """
    批量下载指定分类的画作
    返回一个ZIP文件
    """
    return await batch_download(category=category, db=db)

# 下载指定朝代的画作
@router.get("/batch")
async def batch_download_dynasty(
    dynasty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    批量下载指定朝代的画作
    返回一个ZIP文件
    """
    return await batch_download(dynasty=dynasty, db=db)

# 下载指定作者的画作
@router.get("/batch")
async def batch_download_author(
    author: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    批量下载指定作者的画作
    返回一个ZIP文件
    """
    return await batch_download(author=author, db=db) 