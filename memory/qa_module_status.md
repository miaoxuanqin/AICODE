---
name: 问答助手模块开发状态
description: 问答助手模块的开发进度、已完成文件、待完成事项
type: project
originSessionId: current
lastUpdated: 2026-04-27
---

# 问答助手模块开发状态

> 最后更新：2026-04-27

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
| `src/views/qa/QAChat.vue` | 问答助手页面 |
| `src/views/assistant/LawAssistant.vue` | 执法智能助手 |
| `src/views/assistant/SuperviseAssistant.vue` | 工程监管助手 |

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

| category | 用途 | 页面 | 说明 |
|----------|------|------|------|
| `qa` | 问答助手会话 | QAChat.vue | 只显示 category='qa' 的会话 |
| `law_general` | 执法助手会话 | LawAssistant.vue | 自动过滤掉 |
| `supervise` | 工程监管助手会话 | SuperviseAssistant.vue | 自动过滤掉 |

## 技术方案

### RAG 架构流程
```
用户提问 → Embedding → Qdrant向量搜索/ES关键词搜索 → 检索知识 → 构建Prompt → MiniMax LLM → 返回回答
```

### 不同 category 的搜索策略

| category | 搜索方式 | search_size |
|----------|---------|------------|
| `qa` | Qdrant 向量搜索 | 5 |
| `law_general` | Qdrant 向量搜索 | 5 |
| `supervise` | Qdrant 向量搜索 | 8 |

### LLM 配置
| 配置项 | 值 |
|-------|-----|
| API_BASE | https://api.minimaxi.com/anthropic |
| AUTH_TOKEN | sk-cp-gPTmjYnqdL4ITzqFsdXjUKxaAwD2xyx2WKeidsK1bMHsqv04X7lFwYlpqaO8WyVGYWAW5OV7yE1rA8lzcHDm3s5GGvYtGTXQk-u1WKjRrLETKSmVqUf2p0g |
| MODEL | MiniMax-M2.7 |

## 2026-04-27 完成内容

### 1. LLM 响应问题修复
- **问题**：`"抱歉，回答生成失败"` - MiniMax-M2.7 返回 `ThinkingBlock` 导致 `_call_llm` 无法正确获取 `TextBlock`
- **解决**：正确处理 ThinkingBlock，提取 TextBlock 内容

### 2. Prompt 优化
- **知识内容格式**：从 `【知识 1】标题...内容` 改为 `[1] 标题\n分类：xxx\n内容`
- **系统提示**：三个助手的 system_prompt 都添加了明确指令：
  - "直接整合信息，答案要专业、准确、流畅"
  - "不要在回答中提及【知识1】、【知识2】、参考信息、知识内容等编号或来源"

### 3. 消息时间显示修复
- 后端 `qa_service.py` 返回 `YYYY-MM-DD HH:mm:ss` 格式的完整日期时间
- 前端直接显示 `msg.time`（后端返回的格式）

### 4. 会话管理功能修复（2026-04-27）
- **执法智能助手/工程监管助手**：`clearHistory` 现在会调用 `qaApi.clearMessages()` 清空会话
- **问答助手**：添加了 `deleteSession` 函数支持删除整个会话

### 5. 前端会话过滤修复（2026-04-27）
- 问答助手只显示 `category === 'qa'` 的会话（之前是 `category !== 'law_general'`，导致 supervise 会话混入）

### 6. 后端重启
- 修改代码后需要重启 uvicorn 才能生效

## Bug 修复记录

| 日期 | 问题 | 修复 |
|------|------|------|
| 2026-04-27 | LLM 返回 "抱歉，回答生成失败" | 正确处理 ThinkingBlock |
| 2026-04-27 | 回答中显示【知识1】【知识2】 | Prompt 优化，添加明确指令 |
| 2026-04-27 | 执法/监管助手清空会话无效 | clearHistory 调用 qaApi.clearMessages |
| 2026-04-27 | 问答助手会话列表混入其他类别 | 过滤条件改为 `category === 'qa'` |
| 2026-04-27 | 消息时间只显示时间无日期 | 后端返回完整 `YYYY-MM-DD HH:mm:ss` |

## 待完成
1. 评价功能前端联动
2. 知识库批量导入
3. 性能优化（缓存、预热）
4. 会话混乱问题进一步排查（多标签页同时使用）