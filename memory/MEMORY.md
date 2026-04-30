# Memory Index

- [项目概述](project_overview.md) — 技术栈、架构、外部服务地址
- [知识模块状态](knowledge_module_status.md) — 开发进度、已完成文件、待完成事项（已更新 2026-04-30）
- [问答助手模块状态](qa_module_status.md) — 问答助手、执法助手，工程监管助手、图谱增强问答进度
- [用户偏好](user_preferences.md) — 工作方式偏好、反馈指导

## 文档更新 (2026-04-30)

### 新建文档

| 文档 | 说明 |
|------|------|
| `04-功能详细设计/知识管理-知识管理-原型设计-20260430.md` | 知识管理原型设计规范 |
| `04-功能详细设计/知识管理-门户控制台-原型设计-20260430.md` | 门户控制台原型设计规范 |
| `04-功能详细设计/知识管理-知识管理-新界面详细设计-20260430.md` | 知识管理新界面详细设计 |
| `03-技术架构设计/知识模块-数据存储架构-技术架构设计-20260430.md` | 数据存储架构设计 |
| `08-项目进度/项目-通用-本次迭代内容-进度--20260430.md` | 本次迭代进度（已更新） |

### 更新文档

- `memory/knowledge_module_status.md` — 新增知识管理新界面开发进度
- `memory/MEMORY.md` — 新增文档索引

## Session 内容摘要 (2026-04-30)

### 知识管理新界面开发

**完成内容**：
1. **Vue组件开发** - KnowledgeManageNew.vue（基于HTML原型转换）
2. **路由配置** - `/knowledge/manage-new`
3. **菜单配置** - MainLayout.vue 新增"知识管理(新)"
4. **API开发** - stats/rebuild/clear 接口
5. **数据库迁移** - 新增 es_indexed/vector_indexed/graph_indexed 列

**访问路径**：
- 原有界面：`/knowledge/manage`
- 新界面：`/knowledge/manage-new`（左侧菜单"知识管理(新)"）

**后端接口**：
| 接口 | 方法 | 说明 |
|------|------|------|
| `/knowledge/stats` | GET | 获取知识统计（总数、ES索引数、向量数、图谱数） |
| `/knowledge/{id}/rebuild/{type}` | POST | 重建指定索引 |
| `/knowledge/{id}/clear/{type}` | DELETE | 清空指定索引 |

**Bug修复**：
1. `ClockIsEmpty` icon 不存在 - 已移除导入
2. API响应结构 `res.data.items` 错误 - 改为 `res.items`
3. 选择框宽度不一致 - 添加固定宽度样式

### 知识类型

| 类型 | 值 | 存储 |
|------|-----|------|
| PDF文档 | `pdf` | MinIO + ES解析文本 |
| Word文档 | `doc` | MinIO + ES解析文本 |
| 文本 | `html` | ES原始文本 |

### 数据存储架构

| 存储介质 | 存储内容 | 说明 |
|---------|---------|------|
| MySQL | 元数据 | id/title/type/category/source/tags/file_path/created_at（不存内容） |
| ES | 内容 | doc/pdf类型存解析文本，text类型存原始文本 |
| 向量库 | 向量 | 文本向量化用于语义搜索 |
| 知识图谱 | 实体关系 | 节点和边 |
| MinIO | 原始文件 | 仅 doc/pdf 类型 |

### 已完成文件

- `code/frontend/src/views/knowledge/KnowledgeManageNew.vue` — 知识管理新界面Vue组件
- `code/frontend/src/views/knowledge/KnowledgeManageNew.html` — 知识管理原型（参考）
- `code/frontend/src/views/Portal.html` — 门户控制台原型（未集成）

### 待完成事项

- [ ] 完善知识编辑功能
- [ ] 实现文件预览功能（PDF.js / mammoth.js）
- [ ] 将 Portal.html 集成到 Vue 项目中作为实际首页
- [ ] 对接后端 API 获取真实数据