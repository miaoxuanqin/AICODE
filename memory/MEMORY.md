# Memory Index

- [项目概述](project_overview.md) — 技术栈、架构、外部服务地址
- [知识模块状态](knowledge_module_status.md) — 开发进度、已完成文件、待完成事项
- [问答助手模块状态](qa_module_status.md) — 问答助手、执法助手、工程监管助手、图谱增强问答进度
- [用户偏好](user_preferences.md) — 工作方式偏好、反馈指导

## 文档更新 (2026-04-28)

### 新建文档
- [Neo4j集成方案详细设计](c:/AICODE3/04-功能详细设计/智能助手-图谱增强问答-Neo4j集成方案-详细设计--20260428.md) — 实体类型、关系类型、抽取策略、服务设计、API接口
- [Neo4j图数据库架构设计](c:/AICODE3/03-技术架构设计/知识模块-Neo4j图数据库架构-技术架构设计--20260428.md) — 数据模型、服务架构、删除逻辑、部署架构
- [Neo4j集成开发参考](c:/AICODE3/06-开发参考/知识模块-Neo4j集成-开发参考--20260428.md) — 环境准备、服务说明、API接口、调试方法

### 更新文档
- [知识模块状态](c:/AICODE3/memory/knowledge_module_status.md) — 2026-04-28 更新（Neo4j集成完成）
- [图谱增强问答详细设计](c:/AICODE3/04-功能详细设计/智能助手-图谱增强问答-详细设计--20260428.md) — 更新（Neo4j集成规划）
- [图谱增强RAG架构设计](c:/AICODE3/03-技术架构设计/知识模块-图谱增强RAG架构-技术架构设计--20260428.md) — 更新（Neo4j混合架构）
- [图谱增强RAG开发参考](c:/AICODE3/06-开发参考/知识模块-图谱增强RAG-开发参考--20260428.md) — 更新（Neo4j开发指南）
- [图谱增强问答进度](c:/AICODE3/08-项目进度/智能助手-图谱增强问答-进度--20260428.md) — 2026-04-28 更新（Neo4j集成开发完成）

## 2026-04-28 Session 内容摘要

### Neo4j 集成开发

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

## 2026-04-27 完成内容摘要

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
