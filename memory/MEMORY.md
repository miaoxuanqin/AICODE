# Memory Index

- [项目概述](project_overview.md) — 技术栈、架构、外部服务地址
- [知识模块状态](knowledge_module_status.md) — 开发进度、已完成文件、待完成事项（已更新 2026-05-04）
- [问答助手模块状态](qa_module_status.md) — 问答助手、执法助手，工程监管助手、图谱增强问答进度
- [用户偏好](user_preferences.md) — 工作方式偏好、反馈指导

## 文档更新 (2026-05-04)

### 新建文档

| 文档 | 说明 |
|------|------|
| `04-功能详细设计/统计分析门户-数据统计分析-详细设计--20260504.md` | 统计分析门户页面详细设计 |
| `08-项目进度/统计分析门户-数据统计分析-进度--20260504.md` | 统计分析门户开发进度 |

### 更新文档

- `memory/knowledge_module_status.md` — 新增门户原型开发内容、更新完成度
- `memory/MEMORY.md` — 更新文档索引

## Session 内容摘要 (2026-05-04)

### 统计分析门户原型开发

**完成内容**：
1. 全新的 PortalPage.vue 统计分析门户页面
2. 6个统计卡片：知识总数、本月新增、全文索引量、向量索引量、图谱节点数、用户总数
3. 6个可交互图表：
   - 知识增长趋势（面积折线图，支持周/月/年切换）
   - 分类分布（环形图/玫瑰图切换）
   - 索引状态分布（堆叠柱状图）
   - 热门标签TOP15（水平柱状图/词云切换）
   - 知识来源TOP10（渐变柱状图）
   - 用户活跃度趋势（热力日历图）
4. 快捷操作入口（渐变图标卡片）
5. 动态时间线 + 实时索引进度条

**设计特点**：
- 渐变紫色标题栏 (#667eea → #764ba2)
- 卡片悬停动效和微交互
- 响应式布局（支持多种屏幕尺寸）
- 玻璃态效果和阴影层次

**技术实现**：
- ECharts 5.x 图表库
- Element Plus 组件
- Vue 3 Composition API

**修改的文件**：
- `code/frontend/src/views/portal/PortalPage.vue` — 完全重写

**访问地址**：
- http://localhost:3001/portal

---

## Session 内容摘要 (2026-05-03)

### 分类树功能开发

**完成内容**：
1. Category 模型 + API（树形结构）
2. 左侧分类树侧边栏（220px）
3. 分类 CRUD 管理弹窗
4. 点击分类节点筛选知识列表

**修改的文件**：
- `code/backend/app/models/category.py` — 新建
- `code/backend/app/api/v1/category.py` — 新建
- `code/backend/app/schemas/category.py` — 新建
- `code/frontend/src/api/index.js` — 新增 categoryApi
- `code/frontend/src/views/knowledge/KnowledgeManageNew.vue` — 分类树 + 布局修复

**Bug修复**：
1. `categoryApi is not defined` — 导入缺失
2. 页面布局错乱（所有内容排成一列）— `</div>` 提前关闭导致嵌套错误
3. `asyncio.create_task` 在同步函数中不执行 — 改用 threading.Thread
4. 搜索筛选参数不生效 — 后端新增参数 + 前端补充传递
5. Word 文档类型 `doc` → `docx`

### 后端 API 验证

两个 500 错误接口已验证正常：
- `GET /api/v1/knowledge` → 返回 43 条数据
- `GET /api/v1/knowledge/stats` → `{"total":43,"esIndexed":39,"vectorDone":39,"graphDone":42}`

---

## Session 内容摘要 (2026-05-02)

### PDF/Word/文本预览功能修复

**完成内容**：
1. PDF 预览功能修复 - pdfjs-dist worker 加载问题
2. 文本类型知识预览 - 无 file_path 的知识直接获取 content
3. 下载按钮控制 - 文本类型不显示下载按钮
4. 图谱重建接口修复 - 从 ES 而非 MySQL 获取 content

**技术要点**：
- pdfjs-dist 5.7.284 worker 动态加载
- mammoth 1.12.0 Word 转 HTML
- 容器等待循环解决弹窗渲染时序问题

---

## Session 内容摘要 (2026-05-01)

### 知识管理新界面开发

**完成内容**：
1. Vue组件开发 - KnowledgeManageNew.vue（基于HTML原型转换）
2. 路由配置 - `/knowledge/manage-new`
3. 菜单配置 - MainLayout.vue 新增"知识管理(新)"
4. API开发 - stats/rebuild/clear 接口
5. 数据库迁移 - 新增 es_indexed/vector_indexed/graph_indexed 列

**访问路径**：
- 原有界面：`/knowledge/manage`
- 新界面：`/knowledge/manage-new`（左侧菜单"知识管理(新)"）
