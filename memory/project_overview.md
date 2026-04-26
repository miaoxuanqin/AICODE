---
name: 住建知识库项目概述
description: 海南省住建知识库项目，技术栈、架构、关键路径等核心信息
type: project
originSessionId: c9493d03-2404-41fa-8b7b-c4643b1160bc
---
# 海南省住建知识库项目

## 项目定位
行业知识图谱模块，为住建和综合执法领域提供知识管理、搜索、智能助手服务。

## 技术栈
- 后端：FastAPI + SQLAlchemy + MySQL + Redis
- 前端：Vue3 + Element Plus + Vue Router + Pinia
- 搜索引擎：Elasticsearch 8.13
- 向量库：Qdrant（暂未接入）
- 文件存储：MinIO (S3兼容)

## 外部服务地址
| 服务 | 地址 |
|-----|------|
| MySQL | 172.20.36.91:3306 |
| Redis | 172.20.36.91:6379 |
| Elasticsearch | 172.20.36.91:9200 |
| Qdrant | 172.20.36.91:6333 |
| MinIO | 172.20.36.91:9000 |

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
| AUTH_TOKEN | sk-cp-gPTmjYnqdL4ITzqFsdXjUKxaAwD2xyx2WKeidsK1bMHsqv04X7lFwYlpqaO8WyVGYWAW5OV7yE1rA8lzcHDm3s5GGvYtGTXQk-u1WKjRrLETKSmVqUf2p0g |
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
5. 语义搜索（Qdrant向量，embedding代码已写但未接入）
6. 热搜词统计（Redis sorted set）
7. 收藏、评论功能
