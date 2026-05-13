# Memory Index

- [项目概述](project_overview.md) — 技术栈、架构、外部服务地址
- [知识模块状态](knowledge_module_status.md) — 开发进度、已完成文件、待完成事项（已更新 2026-05-13）
- [问答助手模块状态](qa_module_status.md) — 问答助手、执法助手，工程监管助手、图谱增强问答进度
- [用户偏好](user_preferences.md) — 工作方式偏好、反馈指导

## 文档更新 (2026-05-13)

### 新建文档

| 文档 | 说明 |
|------|------|
| `02-需求和项目介绍/系统-个人中心-需求--20260513.md` | 个人中心需求文档 |
| `04-功能详细设计/系统-个人中心-详细设计--20260513.md` | 个人中心详细设计 |
| `08-项目进度/系统-个人中心-进度--20260513.md` | 个人中心进度跟踪 |

### 更新文档

| 文档 | 更新内容 |
|------|---------|
| `memory/knowledge_module_status.md` | 新增个人中心模块、PortalPage修复、knowledge.py修复 |
| `code/frontend/src/views/UserCenter.vue` | 新建个人中心页面 |
| `code/frontend/src/router/index.js` | 添加 /user/center 路由 |
| `code/frontend/src/components/layout/MainLayout.vue` | 右上角"个人中心"链接改为跳转 |

---

## Session 内容摘要 (2026-05-13)

### 个人中心模块

**完成内容**：
1. 需求文档：`02-需求和项目介绍/系统-个人中心-需求--20260513.md`
2. 详细设计：`04-功能详细设计/系统-个人中心-详细设计--20260513.md`
3. 前端页面：`code/frontend/src/views/UserCenter.vue`
4. 路由配置：`code/frontend/src/router/index.js` - 添加 /user/center
5. 菜单配置：右上角头像下拉菜单"个人中心"改为跳转到 /user/center

**待完成**：
- 后端 API：`/users/{id}/favorites`、`/users/{id}/comments`

### PortalPage.vue Bug 修复

**问题**：
1. `updateActivityChart is not defined` - 函数缺失
2. 评论接口 500 错误 - `CommentItem.user_id` 类型定义错误
3. 评论按钮无法跳转到评论区

**修复**：
- 添加缺失的 `updateActivityChart` 函数
- `CommentItem.user_id` 从 `str` 改为 `int`
- 评论按钮改为 `scrollIntoView` 滚动到评论区
- `onMounted` 改为 `async/await` 顺序加载
- 添加 `watch` 监听路由变化重新加载

### knowledge.py API 修复

**问题**：`filter(True)` 在 SQLAlchemy 中无效

**修复**：改用条件分支分别构建查询
- `get_portal_stats` 接口
- `get_index_progress` 接口

### start-dev.bat 更新

**问题**：中文编码乱码导致脚本执行失败

**修复**：改用纯 ASCII 编码，路径改为绝对路径 `C:\AICODE3\code\...`

---

## Session 内容摘要 (2026-05-04)

### 统计分析门户后端API对接

**完成内容**：
1. 新增 `/api/v1/knowledge/stats/portal` 接口
2. 新增 `PortalStatsResponse` 等 Schema
3. 修复 MySQL JSON 字段聚合问题
4. 前端 `PortalPage.vue` 连接真实API

### 搜索门户来源筛选修复

**问题**：`filters.source` 定义了但从未传递给 API

**修复**：
- `SearchPortal.vue` - 添加 `if (filters.source) params.source = filters.source`
- `search_service.py` - `search_keyword` 添加 `source` 参数
- `knowledge.py` - 所有 `search_keyword` 调用传递 `source` 参数

---

## Session 内容摘要 (2026-05-03)

### 分类树功能开发

**完成内容**：
1. Category 模型 + API（树形结构）
2. 左侧分类树侧边栏（220px）
3. 分类 CRUD 管理弹窗
4. 点击分类节点筛选知识列表

**Bug修复**：
1. `categoryApi is not defined` — 导入缺失
2. 页面布局错乱 — `</div>` 提前关闭导致嵌套错误
3. `asyncio.create_task` 在同步函数中不执行 — 改用 threading.Thread

---

## Session 内容摘要 (2026-05-02)

### PDF/Word/文本预览功能修复

**完成内容**：
1. PDF 预览功能修复 - pdfjs-dist worker 加载问题
2. 文本类型知识预览 - 无 file_path 的知识直接获取 content
3. 下载按钮控制 - 文本类型不显示下载按钮
4. 图谱重建接口修复 - 从 ES 而非 MySQL 获取 content

---

## Session 内容摘要 (2026-05-01)

### 知识管理新界面开发

**完成内容**：
1. Vue组件开发 - KnowledgeManageNew.vue
2. 路由配置 - `/knowledge/manage-new`
3. 菜单配置 - MainLayout.vue 新增"知识管理(新)"
4. API开发 - stats/rebuild/clear 接口