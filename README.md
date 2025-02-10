# 中国画数据集管理系统

基于 FastAPI + SQLite + SQLAlchemy 的中国画数据集管理系统。

## 功能特点

* 支持中国画作品的上传、下载和管理
* 提供画作元数据管理
* 作者统计分析
* RESTful API 接口
* 自动化文档（Swagger UI）

### 新增功能 (2024.02)

* 集成 DeepSeek API 进行智能分析
  - 使用 DeepSeek-V3 模型进行艺术特征分析
  - 使用 DeepSeek-R1 模型进行学术研究分析
* 画作信息自动补充
  - 基本信息补充
  - 艺术特征分析
  - 文化价值评估
  - 创作背景研究
  - 保存状况记录
* 数据验证功能
  - 时代考证
  - 艺术特征验证
  - 史料核对
  - 完整性检查
* 相关信息搜索
  - 艺术分析（使用 V3 模型）
    - 艺术特征和风格分析
    - 作品历史背景
    - 艺术家生平简介
  - 学术研究（使用 R1 模型）
    - 相关学术研究成果
    - 重要文献记载
    - 艺术史地位评估
    - 参考来源追踪

## 系统要求

* Python 3.11+
* FastAPI
* SQLite
* SQLAlchemy
* OpenAI (用于 DeepSeek API 调用)

## 安装

1. 克隆仓库

```bash
git clone https://github.com/your-username/chinese-painting-dataset-manager.git
cd chinese-painting-dataset-manager
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置环境变量

创建 `.env` 文件并添加以下配置：
```
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

4. 运行应用

```bash
python main.py
```

应用将在 http://localhost:8000 启动，API文档可在 http://localhost:8000/docs 访问。

## 项目结构

```
chinese-painting-dataset-manager/
├── app/                    # 应用主目录
│   ├── api/               # API端点
│   │   ├── paintings.py   # 画作相关API
│   │   └── analytics.py   # 统计分析API
│   ├── core/              # 核心功能
│   │   ├── config.py      # 配置管理
│   │   ├── database.py    # 数据库配置
│   │   └── utils.py       # 工具函数
│   ├── models/            # 数据模型
│   │   ├── paintings.py   # 画作模型
│   │   └── schemas.py     # Pydantic模型
│   └── services/          # 业务服务
│       └── deepseek_service.py  # DeepSeek API服务
├── data/                  # 数据存储目录
├── logs/                  # 日志文件
├── tests/                 # 测试文件
├── frontend/             # 前端文件
│   ├── index.html        # 主页面
│   ├── styles.css        # 样式文件
│   └── app.js           # 前端逻辑
└── main.py               # 应用入口
```

## API文档

启动应用后，访问 http://localhost:8000/docs 查看完整的API文档。

### 主要API端点

* `/api/paintings/` - 画作管理
  - GET: 获取画作列表
  - POST: 创建新画作
  - PUT: 更新画作信息
  - DELETE: 删除画作
* `/api/upload-pair` - 上传图片和JSON文件对
* `/api/analytics/` - 统计分析
  - `/dynasty` - 朝代统计
  - `/category` - 类别统计
  - `/artist` - 艺术家统计
  - `/timeline` - 时间线统计

## 使用示例

### 1. 上传画作

```python
import requests
import json

files = {
    'image': ('painting.jpg', open('painting.jpg', 'rb')),
    'json_file': ('metadata.json', open('metadata.json', 'rb'))
}

response = requests.post('http://localhost:8000/api/upload-pair', files=files)
print(response.json())
```

### 2. 获取画作分析

```python
response = requests.get('http://localhost:8000/api/paintings/1')
painting_data = response.json()
print(json.dumps(painting_data, indent=2, ensure_ascii=False))
```

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。 