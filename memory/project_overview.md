---
name: 住建知识库项目概述
description: 海南省住建知识库项目，技术栈、架构、关键路径等核心信息
type: project
originSessionId: c9493d03-2404-41fa-8b7b-c4643b1160bc
lastUpdated: 2026-04-30
---
# 海南省住建知识库系统

## 项目定位
行业知识图谱模块，为住建和综合执法领域提供知识管理、搜索、智能助手服务。

## 系统名称建议
**海南住建通** — 地域+住建+通达，响亮好记

## 技术栈
- 后端：FastAPI + SQLAlchemy + MySQL + Redis
- 前端：Vue3 + Element Plus + Vue Router + Pinia
- 搜索引擎：Elasticsearch 8.13
- 向量库：Qdrant
- 图数据库：Neo4j（2026-04-27 新增）
- 文件存储：MinIO (S3兼容)
- 大模型：MiniMax-M2.7 / Anthropic

## 外部服务地址
| 服务 | 地址 |
|-----|------|
| MySQL | 172.20.36.91:3306 |
| Redis | 172.20.36.91:6379 |
| Elasticsearch | 172.20.36.91:9200 |
| Qdrant | 172.20.36.91:6333 |
| MinIO | 172.20.36.91:9000 |
| Neo4j | 172.20.36.91:7474 |

## LLM 配置（已接入，embedding 暂未使用）
| 配置项 | 值 |
|-------|-----|
| API_BASE | https://ark.cn-beijing.volces.com/api/coding |
| AUTH_TOKEN | ark-cd684a2-8027-4e45-843e-8fc4345be2cc-336df |
| MODEL | minimax-m2.7 |

## Anthropic LLM 配置（QA 模块使用）
| 配置项 | 值 |
|-------|-----|
| API_BASE | https://api.minimaxi.com/anthropic |
| AUTH_TOKEN | sk-cp-xxx |
| MODEL | MiniMax-M2.7 |

## 项目结构
```
code/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/  # API 路由
│   │   ├── models/  # 数据模型
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # 业务服务
│   │   └── main.py
│   ├── core/         # RBAC
│   ├── cleanup_orphaned.py  # 孤立数据清理
│   └── requirements.txt
└── frontend/        # Vue3 前端
    └── src/
        ├── api/      # API 调用
        ├── views/    # 页面组件
        ├── router/  # 路由配置
        └── components/
```

## 知识模块核心功能
1. 文件上传解析（Word/PDF → MinIO存储，ES存内容）
2. 手动添加知识（富文本编辑器，支持加粗/斜体/列表等格式）
3. 知识 CRUD（MySQL存元数据+摘要，ES存完整内容）
4. 全文搜索（Elasticsearch keyword）
5. 语义搜索（Qdrant向量，已接入）
6. 热搜词统计（Redis sorted set）
7. 收藏、评论功能
8. 图谱增强问答（Graph-RAG，多跳推理，可视化推理路径）
9. Neo4j 图谱浏览（节点交互、关系导航、路径探索）

## 数据存储架构（2026-04-30 更新）

| 存储介质 | 存储内容 | 说明 |
|---------|---------|------|
| MySQL | 元数据 | id/title/type/category/source/tags/file_path/created_at（不存内容） |
| ES | 内容 | doc/pdf类型存解析文本，text类型存原始文本 |
| 向量库 | 向量 | 文本向量化用于语义搜索 |
| 知识图谱 | 实体关系 | 节点和边 |
| MinIO | 原始文件 | 仅 doc/pdf 类型 |

### 知识类型

| 类型 | 值 | 存储 |
|------|-----|------|
| PDF文档 | `pdf` | MinIO + ES解析文本 |
| Word文档 | `doc` | MinIO + ES解析文本 |
| 文本 | `text` | ES原始文本 |

### 索引状态

| 状态字段 | 说明 | 值 |
|---------|------|-----|
| `fullTextStatus` | ES索引状态 | `indexed`/`pending` |
| `vectorStatus` | 向量处理状态 | `done`/`pending` |
| `graphStatus` | 图谱构建状态 | `done`/`pending` |

## 原型文件

| 文件 | 说明 |
|------|------|
| `code/frontend/src/views/knowledge/KnowledgeManageNew.html` | 知识管理新界面原型 |
| `code/frontend/src/views/Portal.html` | 门户控制台原型 |

## 图谱数据（截至 2026-04-29）
| 存储 | 数量 | 状态 |
|------|------|------|
| MySQL | 42 条 | 正常运行 |
| Elasticsearch | 42 条 | 已同步 |
| Qdrant | 42 个向量 | 已同步 |
| Neo4j | 825 节点 / 1352 边 | 已同步 |

## 关键文件
| 文件 | 说明 |
|------|------|
| `code/backend/app/services/graph_service.py` | 图谱服务，包含 reason 和 reason_with_neo4j |
| `code/backend/app/services/neo4j_service.py` | Neo4j 操作服务 |
| `code/backend/app/services/graph_extractor.py` | 实体关系抽取 |
| `code/frontend/src/views/graph/GraphExplorer.vue` | 图谱浏览页面 |
| `code/frontend/src/views/graph/GraphQAChat.vue` | 图谱增强问答页面 |