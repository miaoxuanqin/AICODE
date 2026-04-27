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
- 样式优化：✅ 政务蓝主题已完成

## 已完成文件

### 后端 (code/backend/)
| 文件 | 说明 |
|------|------|
| `app/services/qa_service.py` | 问答服务（RAG架构，ES搜索+向量搜索+MiniMax LLM，session管理） |
| `app/services/graph_service.py` | 图谱服务（Graph-RAG，实体识别，多跳推理） |
| `app/schemas/qa.py` | Pydantic schemas (KnowledgeCard 包含 type+category 字段) |
| `app/models/qa.py` | QARecord, QAHotQuestion, QAHistory, QASession, QASessionMessage 模型 |
| `app/api/v1/qa.py` | 问答助手 API (session管理、chat、stats等) |
| `app/api/v1/graph.py` | Graph API (推理详情 details 字段) |
| `app/services/search_service.py` | ES搜索服务 + Qdrant向量搜索 |
| `app/services/embedding_service.py` | Embedding服务 |

### 前端 (code/frontend/)
| 文件 | 说明 |
|------|------|
| `src/api/index.js` | qaApi + graphApi，timeout=120000ms |
| `src/views/qa/QAChat.vue` | 问答助手页面 |
| `src/views/assistant/LawAssistant.vue` | 执法智能助手（政务蓝样式） |
| `src/views/assistant/SuperviseAssistant.vue` | 工程监管助手（政务蓝样式） |
| `src/views/graph/GraphQAChat.vue` | 图谱增强问答页面（推理详情展开功能） |

### 样式 (code/frontend/src/styles/)
| 文件 | 说明 |
|------|------|
| `common.css` | 政务蓝主题样式（主色#1a3a6b） |

## 数据库表
```sql
qa_records              -- 问答记录表
qa_hot_questions        -- 热门问题表
qa_history              -- 问答历史表
qa_session              -- 会话表
qa_session_message      -- 会话消息表
```

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
| 清空会话消息 | DELETE | /api/v1/qa/session/{id}/messages | ✅ 正常 |

## 会话管理（Category 隔离）
| category | 用途 | 页面 | search_size |
|----------|------|------|-------------|
| `qa` | 问答助手会话 | QAChat.vue | 5 |
| `law_general` | 执法助手会话 | LawAssistant.vue | 5 |
| `supervise` | 工程监管助手会话 | SuperviseAssistant.vue | 8 |

## LLM 配置
| 配置项 | 值 |
|-------|-----|
| API_BASE | https://api.minimaxi.com/anthropic |
| AUTH_TOKEN | sk-cp-... |
| MODEL | MiniMax-M2.7 |
| max_tokens | 2048 |

## 2026-04-27 完成内容

### 1. 卡片显示修复
- **问题**：前端期望 `card.type`，后端只返回 `card.category`
- **解决**：
  - `qa_service.py`：返回 `type` 和 `category` 两个字段
  - `schemas/qa.py`：`KnowledgeCard` 增加 `type: str = ""` 字段

### 2. 会话初始化错误处理
- **问题**：`getSessions` API 失败时未创建新会话，导致空白页面
- **解决**：catch 块中添加创建新会话逻辑

### 3. 会话加载错误处理
- **问题**：`loadSessionHistory` 失败导致页面异常
- **解决**：catch 块中设置 `messages.value = []` 显示空状态

### 4. 时间格式修复
- **问题**：消息时间只显示时间（如 `14:30`）无日期
- **解决**：后端 `strftime("%Y-%m-%d %H:%M")` 返回完整日期时间

### 5. 前端超时调整
- **问题**：API 超时 30s 太短，LLM 响应慢时超时
- **解决**：`api/index.js` timeout 从 30000 改为 120000 (120s)

### 6. LLM max_tokens 调整
- **问题**：max_tokens=1024 可能导致回答被截断
- **解决**：qa_service.py 中改为 2048

### 7. 政务蓝主题样式
- **主色**：`#1a3a6b`
- **辅色**：`#b8860b`（金色点缀）
- **应用范围**：common.css、MainLayout.vue、各助手页面

### 8. 代码清理
- 移除 LawAssistant.vue 中的 console.log 调试语句
- 修复重复代码块

## Bug 修复记录

| 日期 | 问题 | 修复 |
|------|------|------|
| 2026-04-27 | 卡片 type 字段缺失 | 后端同时返回 type 和 category |
| 2026-04-27 | 会话初始化失败空白页面 | 添加错误时创建新会话 |
| 2026-04-27 | 会话加载失败异常 | catch 中设置空消息列表 |
| 2026-04-27 | 消息时间无日期 | 后端返回完整日期时间格式 |
| 2026-04-27 | API 超时 30s | 改为 120s |
| 2026-04-27 | LLM 回答截断 | max_tokens 2048 |
| 2026-04-27 | 控制台日志冗余 | 移除调试 console.log |
| 2026-04-27 | 图谱节点悬停乱跳 | `hoveredNode` 改为 `hoveredNodeId` |
| 2026-04-27 | 图谱节点悬停乱跳 | CSS `scale(1.1)` 与 SVG `translate()` 冲突，移除 |
| 2026-04-27 | 推理详情无法查看 | Pydantic `ReasoningStep` 添加 `details` 字段 |
| 2026-04-27 | 图谱问答 404 | Python `__pycache__` 缓存，清除后重启 |

## 待完成
1. 评价功能前端联动
2. 知识库批量导入
3. 性能优化（缓存、预热）
4. 会话混乱问题进一步排查（多标签页同时使用）
