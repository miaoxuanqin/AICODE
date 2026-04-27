---
name: 知识管理模块开发状态
description: 知识管理模块的开发进度、已完成文件、待完成事项
type: project
originSessionId: c9493d03-2404-41fa-8b7b-c4643b1160bc
lastUpdated: 2026-04-27
---
# 知识管理模块开发状态

> 最后更新：2026-04-27

## 开发进度
- 需求分析：✅ 已完成
- 详细设计：✅ 已完成
- 后端开发：✅ 已完成
- 前端开发：✅ 详情页、搜索门户、管理页面均已完成
- 联调测试：✅ 主要功能已完成

## 已完成文件

### 后端 (code/backend/)
| 文件 | 说明 |
|------|------|
| `app/models/knowledge.py` | Knowledge, UserFavorite, KnowledgeComment 模型 |
| `app/models/qa.py` | QARecord, QAHotQuestion, QAHistory, QASession, QASessionMessage 模型 |
| `app/services/parser_service.py` | PDF/Word 解析服务 |
| `app/services/minio_service.py` | MinIO 文件存储 |
| `app/services/search_service.py` | ES 搜索服务 + Qdrant 向量搜索 |
| `app/services/embedding_service.py` | Embedding 服务（local WSL / minimax 切换） |
| `app/services/qa_service.py` | 问答服务（RAG 架构，**所有助手统一使用向量搜索**） |
| `app/schemas/knowledge.py` | Pydantic schemas |
| `app/schemas/qa.py` | QA Pydantic schemas |
| `app/api/v1/knowledge.py` | 知识管理 API（支持 keyword/vector/hybrid 三种搜索模式） |
| `app/api/v1/qa.py` | 问答助手 API |
| `requirements.txt` | python-docx, pdfplumber, elasticsearch, qdrant-client, minio, anthropic |

### 前端 (code/frontend/)
| 文件 | 说明 |
|------|------|
| `src/api/index.js` | knowledgeApi + qaApi |
| `src/views/knowledge/KnowledgeManage.vue` | 知识管理页面 |
| `src/views/knowledge/SearchPortal.vue` | 搜索门户（支持 keyword/vector/hybrid 切换） |
| `src/views/knowledge/KnowledgeDetail.vue` | 知识详情页 |
| `src/views/qa/QAChat.vue` | 问答助手页面 |
| `src/views/assistant/LawAssistant.vue` | 执法智能助手 |
| `src/views/assistant/SuperviseAssistant.vue` | 工程监管助手 |
| `src/components/layout/MainLayout.vue` | 已添加知识管理菜单 |
| `src/router/index.js` | 路由守卫 |

## 数据库表
```sql
knowledge              -- 知识表
user_favorites        -- 收藏表
knowledge_comments    -- 评论表
qa_records           -- 问答记录表
qa_hot_questions     -- 热门问题表
qa_history           -- 问答历史表
qa_session           -- 会话表（含 category 字段）
qa_session_message    -- 会话消息表
```

## 数据存储架构
- **MySQL**: 存储元数据 (title, summary, category, source, tags, file_path, view_count, favorite_count)
- **Elasticsearch**: 存储完整内容 (content)，支持全文搜索
- **Qdrant**: 存储向量 (768维 text2vec-base-chinese)，支持语义搜索
- **Redis**: 存储热搜词计数
- **MinIO**: 存储原始上传文件

## 搜索实现（2026-04-27 更新）

### 三个助手统一使用向量搜索

| 助手 | Category | 搜索方式 | search_size |
|------|----------|---------|-------------|
| 问答助手 | qa | **向量搜索优先** | 5 |
| 执法智能助手 | law_general | **向量搜索优先** | 5 |
| 工程监管助手 | supervise | **向量搜索优先** | 8 |

### 搜索流程

```
所有助手 → 向量搜索 → (失败) → 关键词搜索
                ↓
        Embedding → Qdrant → 返回知识ID → ES获取详情
```

### Prompt 优化（2026-04-27）

修改了 `_build_prompt` 方法，避免 LLM 在回答中显示"【知识1】"、"【知识2】"等编号：

1. **知识内容格式**：从 `【知识 1】标题...内容` 改为 `[1] 标题\n分类：xxx\n内容`
2. **系统提示**：三个助手的 system_prompt 都添加了明确指令：
   - "直接整合信息，答案要专业、准确、流畅"
   - "不要在回答中提及【知识1】、【知识2】、参考信息、知识内容等编号或来源"

### LLM 调用修复（2026-04-27）

修复了 `_call_llm` 方法，原问题：MiniMax-M2.7 返回的 `ThinkingBlock` 导致无法正确获取 `TextBlock`

```python
# 修复前：只检查 type == 'text'
for block in message.content:
    if hasattr(block, 'type') and block.type == 'text':
        return block.text

# 修复后：正确跳过 thinking 块
for block in message.content:
    if hasattr(block, 'type') and block.type == 'text':
        return block.text
```

## 会话管理

### Category 隔离

| category | 用途 | 页面 | 说明 |
|----------|------|------|------|
| `qa` | 问答助手会话 | QAChat.vue | 只显示 category='qa' 的会话 |
| `law_general` | 执法助手会话 | LawAssistant.vue | 自动过滤掉 |
| `supervise` | 工程监管助手会话 | SuperviseAssistant.vue | 自动过滤掉 |

### 前端会话过滤逻辑（2026-04-27 修复）

```javascript
// 问答助手只显示 qa 类别的会话
sessions.value = (data.items || []).filter(s => s.category === 'qa')

// 执法助手只显示 law_general
const lawSessions = (sessionsData.items || []).filter(s => s.category === 'law_general')

// 工程监管助手只显示 supervise
const superviseSessions = (sessionsData.items || []).filter(s => s.category === 'supervise')
```

## 2026-04-27 完成内容

### 1. 消息时间显示修复
- 后端返回 `YYYY-MM-DD HH:mm:ss` 格式的完整日期时间
- 前端直接显示 `msg.time`（后端返回的格式）

### 2. LLM 响应修复
- 问题：`"抱歉，回答生成失败"` - MiniMax 返回 ThinkingBlock 导致 TextBlock 检测失败
- 解决：正确处理 ThinkingBlock，提取 TextBlock 内容

### 3. 会话删除功能（2026-04-27）
- LawAssistant.vue 和 SuperviseAssistant.vue 的 `clearHistory` 现在会调用 `qaApi.clearMessages()` 清空会话
- QAChat.vue 添加了 `deleteSession` 函数支持删除会话

### 4. Prompt 优化
- 知识内容格式从 `【知识1】标题...` 改为 `[1] 标题\n分类：xxx\n内容`
- 系统提示明确要求不要在回答中提及知识编号

## 待完成
1. 评价功能前端联动
2. 知识库批量导入
3. 性能优化（缓存、预热）