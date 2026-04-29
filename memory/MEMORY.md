# Memory Index

- [项目概述](project_overview.md) — 技术栈、架构、外部服务地址
- [知识模块状态](knowledge_module_status.md) — 开发进度、已完成文件、待完成事项（已更新 2026-04-29）
- [问答助手模块状态](qa_module_status.md) — 问答助手、执法助手、工程监管助手、图谱增强问答进度
- [用户偏好](user_preferences.md) — 工作方式偏好、反馈指导

## 文档更新 (2026-04-29)

### 新建文档

- `08-项目进度/知识浏览-知识图谱-图谱浏览功能优化-进度--20260429.md` — 图谱浏览功能优化进度
- `04-功能详细设计/知识浏览-知识图谱-图谱浏览功能优化-详细设计--20260429.md` — 图谱浏览功能优化详细设计
- `06-开发参考/知识浏览-知识图谱-图谱浏览功能优化-开发参考--20260429.md` — 图谱浏览功能优化开发参考
- `04-功能详细设计/知识浏览-知识图谱-图谱浏览功能增强-详细设计--20260429.md` — 图谱浏览功能增强详细设计
- `08-项目进度/知识浏览-知识图谱-图谱浏览功能增强-进度--20260429.md` — 图谱浏览功能增强进度

### 更新文档

- `memory/knowledge_module_status.md` — 新增图谱浏览功能增强状态、Bug 修复记录
- `memory/MEMORY.md` — 新增增强文档索引

## Session 内容摘要 (2026-04-29)

### 图谱浏览功能交互优化

#### 功能列表
1. **引导探索面板** - 显示示例问题按钮，引导用户探索
2. **图例交互增强** - 悬停显示类型说明和示例节点
3. **搜索图谱联动** - 少量搜索结果直接加载到图谱
4. **智能提示** - 选中节点显示关联统计
5. **快捷入口** - 处罚案例/相关法规/随便看看

#### Bug 修复
| 问题 | 文件 | 修复 |
|------|------|------|
| NEO4J_AVAILABLE 缺失 | neo4j_service.py | 添加 `NEO4J_AVAILABLE = True` |
| Neo4j 5.x 语法不兼容 | neo4j_service.py | 改用 `size([(n)--() | 1])` |
| get_center_nodes 返回空 | neo4j_service.py | 边查询条件改为 `a.name IN $node_names` |
| DataSet 去重错误 | GraphExplorer.vue | 渲染前对 nodes/edges 去重 |
| 字体看不清 | GraphExplorer.vue | 添加 `strokeWidth: 2, strokeColor: '#000000'` |
| 模板语法错误 | GraphExplorer.vue | 重构 el-popover 结构 |

#### 项目启动脚本
- `code/start-dev.bat` - Windows 双击启动
- `code/start-dev.sh` - Linux/Mac 启动
- `06-开发参考/01-开发环境配置.md` - 新增第11节启动脚本说明

#### 端口变更
- 后端端口：8000 → 8001（8000 被占用）
- 更新 `vite.config.js` proxy target