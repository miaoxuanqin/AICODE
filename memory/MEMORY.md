# Memory Index

- [项目概述](project_overview.md) — 技术栈、架构、外部服务地址
- [知识模块状态](knowledge_module_status.md) — 开发进度、已完成文件、待完成事项
- [问答助手模块状态](qa_module_status.md) — 问答助手、执法助手、工程监管助手、图谱增强问答进度（已更新 2026-04-28）
- [用户偏好](user_preferences.md) — 工作方式偏好、反馈指导

## 文档更新 (2026-04-28 晚)

### 新建文档

- `08-项目进度/智能助手模块-进度--20260428.md` — 综合进度文档
- `06-开发参考/知识模块-ES重建索引与WSL服务管理-开发参考--20260428.md` — ES重建索引问题 + WSL服务管理

### 更新文档

- `memory/knowledge_module_status.md` — 更新开发状态、数据同步状态、Neo4j 图谱上下文增强
- `08-项目进度/智能助手模块-进度--20260428.md` — 新增图谱上下文增强内容

## 2026-04-28 (晚) Session 内容摘要

### 图谱上下文增强重构

**问题**：Neo4j 图谱数据只用于前端可视化，没有参与 LLM 回答生成。

**解决方案**：
- 新增 `_build_graph_context` 方法 → 将图谱关系加入 LLM prompt
- 新增 `_match_neo4j_entity` 方法 → 处理书名号差异匹配
- 新增 `_neo4j_entity_exists` 方法

**传给 LLM 的数据结构**：
```
知识内容：
【知识 1】{title}
{content[:500]}
...

=== 知识图谱关系（供参考）===

【实体分类】
  法规：《安全生产许可证条例》, 《建筑法》, ...
  条款：第一条, 第二条, 第三条

【关系链条】
  • 《安全生产许可证条例》 包含 第一条
  • 第一条 包含 《建筑法》
  • ...
```

### 数据同步完成

| 存储 | 数量 | 状态 |
|------|------|------|
| MySQL | 42条 | ✅ |
| ES | 42条 | ✅ |
| Qdrant | 42个 knowledge_id | ✅ |
| Neo4j | 42条已同步，270节点 | ✅ |

### 测试结果

**问题**：安全生产许可证条例怎么办理

| Step | 结果 |
|------|------|
| 实体识别 | `['条例怎么办理', '安全生产许可证条例']` |
| 向量搜索 | 4条知识 |
| Neo4j | **69个节点, 97条边** |
| 图谱上下文 | 已生成 |

### 问题修复

1. **等待时可重复发送问题** — 四个页面统一修复
   - 发送按钮增加 `|| isThinking` 条件
   - 按钮文字变为"等待回答中..."
   - 进度 15%-100% 时显示取消按钮
   - 点击取消后移除消息、停止动画

2. **删除知识时 Qdrant 未清理** — `search_service.delete_knowledge_index` 增加 Qdrant 删除

3. **Word 文档 GBK 编码读取失败** — `parser_service._parse_docx_chunk` 增加多编码尝试

4. **Neo4j 未启动时图谱问答无提示** — 前端增加 neo4jStatus 检查

### ES 重建索引问题

- **问题**：`reindex_es.py` 运行时 38 条知识全部失败
- **错误**：`[1:1190] failed to parse field` 等 JSON 解析错误
- **已尝试**：添加 `clean_for_json` 清理控制字符，仍失败
- **建议**：使用 Python ES 客户端代替 curl，或进一步排查 JSON 序列化

### WSL 服务管理

- 创建 `06-开发参考/docker-services.service` systemd 服务
- 实现 Docker 容器（redis/qdrant/elasticsearch/neo4j）随 WSL 自动启动

### Neo4j 清理

- `fix_neo4j.py` — 删除孤立节点（无 EXTRACTED_FROM 关系）
- `check_neo4j.py` — 检查 Neo4j 状态

### "第78条"幻觉问题

- **结论**：确认为 LLM 幻觉，非数据问题
- **证据**：MySQL/ES 检索结果中均无"第78条"

## 文档更新 (2026-04-28 下午)

### 新建文档

- 无

### 更新文档

- `08-项目进度/智能助手-图谱增强问答-进度--20260428.md` — 更新（节点缩小、边样式优化、第4步详情增强）
- `04-功能详细设计/智能助手-图谱增强问答-前端优化-详细设计--20260428.md` — 更新（第4步详情增强、节点尺寸优化）

## 2026-04-28 Session 内容摘要

### 下午 Session (2026-04-28 下午)

#### 问题修复

1. **图谱初始就有数据**
   - 原因：onMounted 中有 setTimeout 加载 mockGraphData
   - 修复：移除 onMounted 中的模拟数据加载

2. **图谱加载效果不明显**
   - 尝试多种动画方案，最终采用分步添加节点/边
   - 节点400ms间隔，边300ms间隔逐步添加

3. **节点重叠问题**
   - 原因：节点半径过大（35px），布局过密
   - 修复：缩小节点半径（28/30/32px）

4. **边样式不清晰**
   - 原因：边颜色太浅（#dcdfe6）
   - 修复：加深边颜色（#7b8db5），加粗（2.5px），文字加背景

5. **开关和默认设置**
   - 名称：图库推理问答 → 图谱增强问答（保持原名）
   - 开关文字：使用Neo4j → 图谱推理
   - 默认值：false → true（默认开启图谱推理）

6. **第4步等待时间太长**
   - 问题：最后一步"综合知识生成最终回答"体验单调
   - 修复：添加进度条动画 + "整合知识中..."提示 + 趣味提示轮换

#### 趣味提示更新

```javascript
const funTips = [
  '正在知识图谱中查找关联信息...',
  '正在分析实体间的语义关系...',
  '正在构建多跳推理路径...',
  '正在匹配相关法规条款...',
  '正在整合案例判决依据...',
  '正在验证逻辑推导链条...',
  '正在生成结构化回答...',
  '即将完成图谱推理...'
]
```

#### 页面标题和开关

| 项目 | 修改后 |
|------|--------|
| 页面标题 | 图谱增强问答 |
| 开关文字 | 图谱推理 |
| 默认值 | true（开启） |

#### 修改文件

1. `code/frontend/src/views/graph/GraphQAChat.vue`
   - 移除 onMounted 中的 mock 数据加载
   - 添加分步渲染动画（节点400ms，边300ms）
   - 缩小节点半径（28/30/32px）
   - 优化边样式（颜色#7b8db5，宽度2.5px）
   - 第4步详情增强（进度条 + 提示）
   - 开关文字改为"图谱推理"
   - 默认 useNeo4j = true

### 上午 Session (2026-04-28)

#### 新增文件
1. `code/backend/app/services/neo4j_service.py` — Neo4j 连接和 CRUD 操作
2. `code/backend/app/services/graph_extractor.py` — 实体关系抽取（规则 + LLM）
3. `code/backend/app/scripts/sync_history_to_neo4j.py` — 批量同步历史数据脚本

#### 修改文件
1. `code/backend/app/config.py` — 添加 neo4j_uri, neo4j_user, neo4j_password
2. `code/backend/requirements.txt` — 添加 neo4j==5.14.0
3. `code/backend/app/services/graph_service.py` — 添加 reason_with_neo4j() 方法
4. `code/backend/app/api/v1/graph.py` — 添加 Neo4j API（status, entity, path, sync）
5. `code/backend/app/api/v1/knowledge.py` — 添加知识入库/删除时同步 Neo4j

#### 核心功能
1. **Neo4j 服务**：节点/关系 CRUD、图谱查询、引用追踪、智能清理
2. **实体抽取**：规则快速抽取 + LLM 语义抽取
3. **同步钩子**：知识入库自动抽取，删除时自动清理无引用实体
4. **EXTRACTED_FROM 关系**：追踪实体来源，删除时判断 ref_count

#### API 接口
- `POST /api/v1/graph/qa` — 图谱问答（新增 use_neo4j 参数）
- `GET /api/v1/graph/neo4j/status` — 连接状态
- `GET /api/v1/graph/neo4j/entity/{name}` — 实体关联图谱
- `GET /api/v1/graph/neo4j/path` — 两实体间路径
- `POST /api/v1/graph/neo4j/sync/{id}` — 同步知识到 Neo4j

## 2026-04-27 Session 内容

### 智能助手模块修复
1. **LLM 响应问题** — MiniMax ThinkingBlock 处理
2. **Prompt 优化** — 去除【知识1】【知识2】显示
3. **会话管理** — clearHistory/deleteSession 功能
4. **会话过滤** — category === 'qa' 修复
5. **消息时间** — YYYY-MM-DD HH:mm:ss 格式

### 2026-04-27 (下午) - 样式优化与Bug修复
1. **卡片字段修复** — 后端同时返回 type 和 category 字段
2. **会话初始化错误处理** — getSessions 失败时创建新会话
3. **会话加载错误处理** — loadSessionHistory 失败时显示空状态
4. **政务蓝主题** — 统一颜色 #409eff → #1a3a6b
5. **API 超时优化** — 30s → 120s
6. **LLM max_tokens** — 1024 → 2048

### 2026-04-27 (晚) - 图谱增强问答（Graph-RAG）Bug修复
1. **图谱节点乱跳** — `hoveredNode` 响应式问题，改为 `hoveredNodeId`
2. **图谱节点乱跳** — CSS `scale(1.1)` 与 SVG `translate()` 冲突，移除问题CSS
3. **推理详情无法查看** — Pydantic `ReasoningStep` 添加 `details` 字段
4. **图谱问答404** — Python `__pycache__` 缓存问题，清除后重启
5. **推理详情展开功能** — 前端点击步骤查看搜索词和知识列表

### 向量分片功能开发
1. **文档分片向量化** — 500字符/chunk，50字符重叠
2. **Qdrant point ID 修复** — 改用独立 UUID
3. **user_id 类型修复** — 统一字符串类型
4. **批量重建索引** — 33条成功，10条跳过