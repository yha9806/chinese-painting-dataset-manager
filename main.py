from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn
from app.core.database import engine
from app.models.paintings import Base
from app.api.paintings import router as paintings_router
from app.api.analytics import router as analytics_router
from app.core.utils import setup_directories, logger

# 创建必要的目录
setup_directories()

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="中国画数据集管理系统",
    description="基于 FastAPI + SQLite + SQLAlchemy 的中国画数据集管理系统",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 包含路由
app.include_router(paintings_router, prefix="/api", tags=["paintings"])
app.include_router(analytics_router, prefix="/api", tags=["analytics"])

# 自定义API文档路由
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="中国画数据集管理系统 API文档",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

# 挂载静态文件
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>中国画数据集管理系统</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="/static/styles.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/vue@2.6.14"></script>
        <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    </head>
    <body>
        <div id="app"></div>
        <script src="/static/app.js"></script>
    </body>
    </html>
    """

if __name__ == "__main__":
    logger.info("启动中国画数据集管理系统...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) 