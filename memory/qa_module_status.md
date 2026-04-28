---
name: 问答助手模块开发状态
description: 问答助手模块的开发进度、已完成文件、待完成事项
type: project
originSessionId: current
lastUpdated: 2026-04-28
---

# 问答助手模块开发状态

> 最后更新：2026-04-28

## 开发进度

| 模块 | 需求 | 设计 | 后端 | 前端 | 测试 | 完成度 |
|------|------|------|------|------|------|--------|
| 问答助手 | ✅ | ✅ | ✅ | ✅ | ✅ | 100% |
| 执法智能助手 | ✅ | ✅ | ✅ | ✅ | ✅ | 100% |
| 工程监管助手 | ✅ | ✅ | ✅ | ✅ | ✅ | 100% |
| 图谱增强问答 | ✅ | ✅ | ✅ | ✅ | ✅ | 100% |
| Neo4j 集成 | ✅ | ✅ | ✅ | - | - | 90% |

---

## 已完成文件

### 后端 (code/backend/)
| 文件 | 说明 |
|------|------|
| `app/services/qa_service.py` | 问答服务（RAG架构，ES搜索+向量搜索+MiniMax LLM，session管理） |
| `app/services/graph_service.py` | 图谱服务（Graph-RAG，实体识别，多跳推理，reason_with_neo4j） |
| `app/services/neo4j_service.py` | Neo4j 操作服务（节点/关系 CRUD、图谱查询、引用清理） |
| `app/services/graph_extractor.py` | 实体关系抽取服务（规则+LLM 抽取） |
| `app/schemas/qa.py` | Pydantic schemas (KnowledgeCard 包含 type+category 字段) |
| `app/models/qa.py` | QARecord, QAHotQuestion, QAHistory, QASession, QASessionMessage 模型 |
| `app/api/v1/qa.py` | 问答助手 API (session管理、chat、stats等) |
| `app/api/v1/graph.py` | Graph API (推理详情 details 字段、Neo4j API) |
| `app/services/search_service.py` | ES搜索服务 + Qdrant向量搜索（含 delete_knowledge_index 修复） |
| `app/services/embedding_service.py` | Embedding服务 |
| `app/services/parser_service.py` | PDF/Word 解析服务（含多编码支持） |

### 前端 (code/frontend/)
| 文件 | 说明 |
|------|------|
| `src/api/index.js` | qaApi + graphApi + neo4jStatus，timeout=120000ms |
| `src/views/qa/QAChat.vue` | 问答助手页面（思考过程展示+取消功能） |
| `src/views/assistant/LawAssistant.vue` | 执法智能助手（思考过程展示+取消功能） |
| `src/views/assistant/SuperviseAssistant.vue` | 工程监管助手（思考过程展示+取消功能） |
| `src/views/graph/GraphQAChat.vue` | 图谱增强问答页面（Neo4j状态检查+取消功能） |

---

## 会话管理（Category 隔离）
| category | 用途 | 页面 | search_size |
|----------|------|------|-------------|
| `qa` | 问答助手会话 | QAChat.vue | 5 |
| `law_general` | 执法助手会话 | LawAssistant.vue | 5 |
| `supervise` | 工程监管助手会话 | SuperviseAssistant.vue | 8 |
| `graph` | 图谱增强问答会话 | GraphQAChat.vue | - |

---

## API 接口
| 接口 | 方法 | 路径 | 状态 |
|------|------|------|------|
| 问答对话 | POST | /api/v1/qa/chat | ✅ |
| 问答统计 | GET | /api/v1/qa/stats | ✅ |
| 热门问题 | GET | /api/v1/qa/hot-questions | ✅ |
| 评价 | POST | /api/v1/qa/rate | ✅ |
| 历史记录 | GET | /api/v1/qa/history | ✅ |
| 创建会话 | POST | /api/v1/qa/session | ✅ |
| 获取会话列表 | GET | /api/v1/qa/sessions | ✅ |
| 获取会话详情 | GET | /api/v1/qa/sessions/{id} | ✅ |
| 删除会话 | DELETE | /api/v1/qa/sessions/{id} | ✅ |
| 清空会话消息 | DELETE | /api/v1/qa/session/{id}/messages | ✅ |
| 图谱问答 | POST | /api/v1/graph/qa | ✅ |
| Neo4j 状态 | GET | /api/v1/graph/neo4j/status | ✅ |
| 实体图谱 | GET | /api/v1/graph/neo4j/entity/{name} | ✅ |
| 路径查询 | GET | /api/v1/graph/neo4j/path | ✅ |
| 同步到Neo4j | POST | /api/v1/graph/neo4j/sync/{id} | ✅ |

---

## LLM 配置
| 配置项 | 值 |
|-------|-----|
| API_BASE | https://api.minimaxi.com/anthropic |
| AUTH_TOKEN | sk-cp-... |
| MODEL | MiniMax-M2.7 |
| max_tokens | 2048 |

---

## 2026-04-28 完成内容

### 1. 思考过程展示（四个页面统一）
- 动态进度条（0-100%）
- 步骤列表（各助手 3-4 步骤）
- 趣味提示语轮换
- 各助手独特主题色

### 2. 取消功能（四个页面统一）
- 进度 > 15% 且 < 100% 显示取消按钮
- 点击后移除消息、停止动画

### 3. 等待时禁止发送（四个页面统一）
- 发送按钮增加 `|| isThinking` 判断
- 按钮文字变为"等待回答中..."

### 4. 删除知识时 Qdrant 清理
- `search_service.delete_knowledge_index` 增加 Qdrant 删除逻辑

### 5. Neo4j 状态检查
- GraphQAChat.vue mount 时检查 Neo4j 连接状态
- 未连接时显示红色警告提示

### 6. Word 文档多编码支持
- `parser_service._parse_docx_chunk` 支持 utf-8/gbk/gb2312/latin-1

---

## Bug 修复记录

| 日期 | 问题 | 修复 |
|------|------|------|
| 2026-04-28 | 等待时可重复发送问题 | 按钮增加 `\|\| isThinking` |
| 2026-04-28 | 删除知识时 Qdrant 未清理 | search_service 增加 Qdrant 删除 |
| 2026-04-28 | Word 文档 GBK 编码失败 | parser_service 增加多编码尝试 |
| 2026-04-28 | Neo4j 未启动无提示 | 前端 neo4jStatus 检查 |
| 2026-04-28 | "第78条"幻觉 | 确认为 LLM 幻觉，非数据问题 |
| 2026-04-27 | 卡片 type 字段缺失 | 后端同时返回 type 和 category |
| 2026-04-27 | 会话初始化失败空白页面 | 添加错误时创建新会话 |
| 2026-04-27 | 会话加载失败异常 | catch 中设置空消息列表 |
| 2026-04-27 | 消息时间无日期 | 后端返回完整日期时间格式 |
| 2026-04-27 | API 超时 30s | 改为 120s |
| 2026-04-27 | LLM 回答截断 | max_tokens 2048 |
| 2026-04-27 | 图谱节点悬停乱跳 | `hoveredNode` 改为 `hoveredNodeId` |
| 2026-04-27 | 图谱节点悬停乱跳 | CSS `scale(1.1)` 与 SVG 冲突，移除 |
| 2026-04-27 | 推理详情无法查看 | Pydantic `ReasoningStep` 添加 `details` |
| 2026-04-27 | 图谱问答 404 | 清除 __pycache__ 后重启 |

---

## 待完成
1. ES 从 MySQL 重建索引（document_parsing_exception 问题）
2. Neo4j 历史数据批量同步
3. "第78条"幻觉问题验证修复
4. 评价功能前端联动
