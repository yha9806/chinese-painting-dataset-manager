# 中国画数据集管理系统

基于 FastAPI + SQLite + SQLAlchemy 的中国画数据集管理系统。

## 功能特点

- 支持中国画作品的上传、下载和管理
- 提供画作元数据管理
- 作者统计分析
- RESTful API 接口
- 自动化文档（Swagger UI）

## 系统要求

- Python 3.11+
- FastAPI
- SQLite
- SQLAlchemy

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

3. 运行应用
```bash
python main.py
```

应用将在 http://localhost:8000 启动，API文档可在 http://localhost:8000/docs 访问。

## 项目结构

```
chinese-painting-dataset-manager/
├── app/                    # 应用主目录
│   ├── api/               # API端点
│   ├── core/              # 核心功能
│   └── models/            # 数据模型
├── data/                  # 数据存储目录
├── logs/                  # 日志文件
├── tests/                 # 测试文件
└── main.py               # 应用入口
```

## API文档

启动应用后，访问 http://localhost:8000/docs 查看完整的API文档。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
```

