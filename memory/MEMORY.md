# Memory Index

- [项目概述](project_overview.md) — 技术栈、架构、外部服务地址
- [知识模块状态](knowledge_module_status.md) — 开发进度、已完成文件、待完成事项（已更新 2026-05-02）
- [问答助手模块状态](qa_module_status.md) — 问答助手、执法助手，工程监管助手、图谱增强问答进度
- [用户偏好](user_preferences.md) — 工作方式偏好、反馈指导

## 文档更新 (2026-05-02)

### 新建文档

| 文档 | 说明 |
|------|------|
| `08-项目进度/知识管理-知识管理新界面-预览功能与文件类型处理-进度-20260502.md` | 预览功能修复进度 |
| `04-功能详细设计/知识管理-知识管理新界面-预览功能与文件类型处理-详细设计-20260502.md` | 预览功能详细设计 |

### 更新文档

- `memory/knowledge_module_status.md` — 新增预览功能修复内容
- `memory/MEMORY.md` — 新增文档索引

## Session 内容摘要 (2026-05-02)

### PDF/Word/文本预览功能修复

**完成内容**：
1. PDF 预览功能修复 - pdfjs-dist worker 加载问题
2. 文本类型知识预览 - 无 file_path 的知识直接获取 content
3. 下载按钮控制 - 文本类型不显示下载按钮
4. 图谱重建接口修复 - 从 ES 而非 MySQL 获取 content

**修改的文件**：
- `code/frontend/src/views/knowledge/KnowledgeManageNew.vue` — 预览功能
- `code/backend/app/api/v1/knowledge.py` — rebuild 接口

**技术要点**：
- pdfjs-dist 5.7.284 worker 动态加载
- mammoth 1.12.0 Word 转 HTML
- 容器等待循环解决弹窗渲染时序问题

### 知识类型与存储

| 类型 | file_type | 存储 |
|------|-----------|------|
| PDF文档 | `pdf` | MinIO + ES解析文本 |
| Word文档 | `doc/docx` | MinIO + ES解析文本 |
| 文本 | `html` | ES原始文本（无file_path） |

---

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

---

### 已完成文件

- `code/frontend/src/views/knowledge/KnowledgeManageNew.vue` — 知识管理新界面Vue组件
- `code/frontend/src/views/knowledge/KnowledgeManageNew.html` — 知识管理原型（参考）
- `code/frontend/src/views/Portal.html` — 门户控制台原型（未集成）

### 待完成事项

- [ ] 完善知识编辑功能
- [ ] 将 Portal.html 集成到 Vue 项目中作为实际首页