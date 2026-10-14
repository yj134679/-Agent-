# AI 内容运营助手 - 后端服务

基于 LangGraph 1.0+ 和 FastAPI 构建的自动化内容生成工作流服务。

## 功能特性

- **AI 选题生成**: 根据主题方向自动生成候选选题
- **AI 文章撰写**: 根据选定选题生成技术文章
- **Human-in-the-loop**: 支持人工介入的选题和审稿机制
- **配图生成**: 自动提取视觉要点并生成配图
- **状态持久化**: 使用 PostgreSQL 持久化工作流状态

## 技术栈

- **Python 3.10+**
- **FastAPI** - 异步 Web 框架
- **LangGraph 1.0+** - 工作流编排
- **PostgreSQL** - 数据持久化
- **SQLAlchemy** - 异步 ORM
- **Pydantic** - 数据验证

## 快速开始

### 1. 环境准备

确保本地已安装并运行 PostgreSQL：

```bash
# Windows - 确认 PostgreSQL 服务运行
# 可以在服务管理器中查看 postgresql 服务状态

# 创建数据库
psql -U postgres -c "CREATE DATABASE aicontent;"
```

### 2. 安装依赖

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 3. 配置环境变量

编辑 `.env` 文件，修改数据库连接信息：

```env
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/aicontent
POSTGRES_URI=postgresql://postgres:your_password@localhost:5432/aicontent
```

### 4. 启动服务

```bash
# 方式 1: 使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式 2: 直接运行
python -m app.main
```

### 5. 访问 API 文档

打开浏览器访问: http://localhost:8000/docs

## API 接口

### 启动工作流

```bash
POST /api/v1/workflow/start
Content-Type: application/json

{
    "topic_direction": "AI技术"
}
```

**响应示例:**

```json
{
    "thread_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "topics_generated",
    "generated_topics": [
        "LangGraph入门：构建你的第一个AI工作流 - AI技术方向",
        "AI Agent实战：从零搭建智能助手 - AI技术方向",
        "Python高并发编程：asyncio深度解析 - AI技术方向"
    ],
    "message": "工作流已启动，请选择一个选题继续"
}
```

### 获取工作流状态

```bash
GET /api/v1/workflow/state/{thread_id}
```

### 恢复工作流 - 选择选题

```bash
POST /api/v1/workflow/resume/{thread_id}
Content-Type: application/json

{
    "action": "select_topic",
    "data": {
        "selected_topic": "LangGraph入门：构建你的第一个AI工作流"
    }
}
```

### 恢复工作流 - 审核通过

```bash
POST /api/v1/workflow/resume/{thread_id}
Content-Type: application/json

{
    "action": "approve"
}
```

### 恢复工作流 - 审核驳回

```bash
POST /api/v1/workflow/resume/{thread_id}
Content-Type: application/json

{
    "action": "reject",
    "data": {
        "feedback": "请增加更多实际代码示例"
    }
}
```

## 工作流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                         START                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     plan_topics                                  │
│                  (AI 生成 3-5 个选题)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              ⏸️ INTERRUPT: human_select_topic                    │
│                    (等待人工选题)                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      write_draft                                 │
│                  (AI 根据选题写长文)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              ⏸️ INTERRUPT: human_review                          │
│                    (等待人工审稿)                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
         [approved]                      [rejected]
              │                               │
              ▼                               │
┌─────────────────────────┐                   │
│    extract_visuals      │                   │
│    (提炼图片要点)        │                   │
└─────────────────────────┘                   │
              │                               │
              ▼                               │
┌─────────────────────────┐                   │
│    generate_images      │                   │
│    (生成配图)           │                   │
└─────────────────────────┘                   │
              │                               │
              ▼                               │
┌─────────────────────────┐                   │
│          END            │◀──────────────────┘
│       (工作流完成)       │    (回到 write_draft 重写)
└─────────────────────────┘
```

## 项目结构

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── workflow.py      # 核心 API 接口
│   ├── core/
│   │   ├── config.py            # 配置管理
│   │   └── db.py                # 数据库连接
│   ├── graph/
│   │   ├── nodes/               # LangGraph 节点
│   │   │   ├── planner.py       # 选题规划
│   │   │   ├── writer.py        # 文章撰写
│   │   │   ├── visualizer.py    # 视觉内容
│   │   │   └── human.py         # 人工介入
│   │   ├── state.py             # 状态定义
│   │   ├── workflow.py          # 工作流组装
│   │   └── utils.py             # 工具函数
│   ├── services/
│   │   ├── llm_service.py       # LLM 服务 (火山引擎 Doubao)
│   │   └── image_service.py     # 图片生成服务
│   └── main.py                  # 应用入口
├── scripts/
│   └── init_db.sql              # 数据库初始化脚本
├── requirements.txt
├── .env
└── README.md
```

## 注意事项

1. **数据库连接**: 确保 PostgreSQL 服务运行且可访问
2. **LLM 配置**: 在 `.env` 中配置火山引擎 Doubao API Key
3. **状态持久化**: LangGraph Checkpointer 会自动创建所需表结构

## License

MIT
