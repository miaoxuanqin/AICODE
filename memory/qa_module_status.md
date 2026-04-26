---
name: 问答助手模块开发状态
description: 问答助手模块的开发进度、已完成文件、待完成事项
type: project
originSessionId: current
---

# 问答助手模块开发状态

> 最后更新：2026-04-26

## 开发进度
- 需求分析：✅ 已完成
- 详细设计：✅ 已完成
- 后端开发：✅ 已完成
- 前端开发：✅ 已完成（问答助手、执法智能助手、工程监管助手）
- 数据库层：✅ 已完成
- 联调测试：✅ 已通过

## 已完成文件

### 后端 (code/backend/)
| 文件 | 说明 |
|------|------|
| `app/services/qa_service.py` | 问答服务（RAG架构，ES搜索+向量搜索+MiniMax LLM，session管理） |
| `app/schemas/qa.py` | Pydantic schemas (QAChatRequest/Response, QASession等) |
| `app/models/qa.py` | QARecord, QAHotQuestion, QAHistory, QASession, QASessionMessage 模型 |
| `app/api/v1/qa.py` | 问答助手 API (session管理、chat、stats等) |
| `app/services/search_service.py` | ES搜索服务 + Qdrant向量搜索 |
| `app/services/embedding_service.py` | Embedding服务 (local WSL / minimax) |

### 前端 (code/frontend/)
| 文件 | 说明 |
|------|------|
| `src/api/index.js` | qaApi (chat, stats, hotQuestions, rate, history, session管理) |
| `src/views/qa/QAChat.vue` | 问答助手页面（消息顺序修复） |
| `src/views/assistant/LawAssistant.vue` | 执法智能助手（初始化逻辑修复，category='law_general'） |
| `src/views/assistant/SuperviseAssistant.vue` | 工程监管助手（后端RAG对接，category='supervise'） |

## 数据库表
```sql
qa_records              -- 问答记录表
qa_hot_questions        -- 热门问题表
qa_history              -- 问答历史表
qa_session              -- 会话表（id, user_id, title, category, is_active, created_at, updated_at）
qa_session_message      -- 会话消息表（id, session_id, role, content, created_at）
```

## 数据存储架构
- **MySQL**: 存储问答记录、热门问题统计、用户历史、会话消息
- **Elasticsearch**: 存储知识内容，提供关键词搜索
- **Qdrant**: 存储向量，支持语义搜索
- **LLM**: MiniMax-M2.7 生成回答

## API 接口
| 接口 | 方法 | 路径 | 状态 |
|------|------|------|------|
| 问答对话 | POST | /api/v1/qa/chat | ✅ 正常 |
| 问答统计 | GET | /api/v1/qa/stats | ✅ 正常 |
| 热门问题 | GET | /api/v1/qa/hot-questions | ✅ 正常 |
| 评价 | POST | /api/v1/qa/rate | ✅ 正常 |
| 历史记录 | GET | /api/v1/qa/history | ✅ 正常 |
| 创建会话 | POST | /api/v1/qa/session | ✅ 正常 |
| 获取会话列表 | GET | /api/v1/qa/sessions | ✅ 正常 |
| 获取会话详情 | GET | /api/v1/qa/sessions/{id} | ✅ 正常 |
| 删除会话 | DELETE | /api/v1/qa/sessions/{id} | ✅ 正常 |

## 会话管理（Category 隔离）

不同助手使用不同的 category 实现会话隔离：

| category | 用途 | 页面 | 搜索方式 |
|----------|------|------|---------|
| `qa` | 问答助手会话 | QAChat.vue | ES关键词搜索 |
| `law_general` | 执法助手会话 | LawAssistant.vue | ES关键词搜索 |
| `supervise` | 工程监管助手会话 | SuperviseAssistant.vue | **Qdrant向量搜索** |

## 技术方案

### RAG 架构流程
```
用户提问 → Embedding → Qdrant向量搜索/ES关键词搜索 → 检索知识 → 构建Prompt → MiniMax LLM → 返回回答
```

### 不同 category 的搜索策略

| category | 搜索方式 | search_size |
|----------|---------|------------|
| `qa` | ES 关键词搜索 | 5 |
| `law_general` | ES 关键词搜索 | 5 |
| `supervise` | **Qdrant 向量搜索** | 8 |

### LLM 配置
| 配置项 | 值 |
|-------|-----|
| API_BASE | https://ark.cn-beijing.volces.com/api/coding |
| AUTH_TOKEN | ark-cd684a2-8027-4e45-843e-8fc4345be2cc-336df |
| MODEL | minimax-m2.7 |

## 2026-04-26 完成内容

### 向量搜索集成
- **qa_service.py** supervise 类别自动使用向量搜索
- 其他类别使用 ES 关键词搜索
- CATEGORY_CONFIG 配置差异化 system_prompt 和 search_size

### 工程监管助手专属配置
```python
CATEGORY_CONFIG = {
    "supervise": {
        "name": "工程监管助手",
        "system_prompt": """你是一个工程监管领域的专家，专注于工程质量安全监督管理工作。
熟悉以下方面的专业知识：
- 建设工程质量管理条例
- 安全生产管理条例
- 施工现场安全技术规范
- 工程质量验收标准
- 常见质量问题识别与处置""",
        "search_size": 8  #比其他场景多3条知识
    }
}
```

### Bug 修复
1. **问答助手消息顺序错乱** - 添加 currentRequestId 追踪 + timestamp 排序
2. **执法智能助手初始化为空** - 重构 initSession，先加载已有会话
3. **普通用户访问管理页面 403** - 路由守卫检查 requireAdmin
4. **知识详情页 HTML 标签显示** - 使用 v-html 代替 {{ }}

### 功能开发
1. **手动添加知识功能** - POST /api/v1/knowledge/manual
2. **工程监管助手后端对接** - category='supervise' 隔离

## 待完成
1. ~~语义搜索~~ ✅ 已完成（工程监管助手向量搜索）
2. ~~Qdrant 向量搜索集成~~ ✅ 已完成
3. 富文本编辑器图片上传功能
4. 评价功能前端数据联动
