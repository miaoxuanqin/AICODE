<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>知识管理 - 新版原型</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/element-plus@2.4.4/dist/index.css">
  <script src="https://cdn.jsdelivr.net/npm/vue@3.3.11/dist/vue.global.prod.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/element-plus@2.4.4/dist/index.full.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/index.iife.min.js"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'PingFang SC', 'Microsoft YaHei', -apple-system, sans-serif;
      background: #f5f7fa;
      min-height: 100vh;
    }
    .app-container { display: flex; }
    .sidebar {
      width: 220px;
      background: linear-gradient(180deg, #1a3a6b 0%, #0d1f3c 100%);
      min-height: 100vh;
      padding: 20px 0;
      color: #fff;
    }
    .logo {
      padding: 0 20px 30px;
      border-bottom: 1px solid rgba(255,255,255,0.1);
      margin-bottom: 20px;
    }
    .logo h1 { font-size: 18px; font-weight: 600; }
    .logo span { font-size: 12px; opacity: 0.6; }
    .nav-item {
      padding: 12px 20px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all 0.2s;
      font-size: 14px;
    }
    .nav-item:hover { background: rgba(255,255,255,0.1); }
    .nav-item.active {
      background: rgba(64,158,255,0.3);
      border-left: 3px solid #409eff;
    }
    .nav-item svg { width: 18px; height: 18px; }
    .main-content {
      flex: 1;
      padding: 24px;
      overflow-x: hidden;
    }
    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }
    .page-title { font-size: 24px; font-weight: 600; color: #1a3a6b; }
    .header-actions { display: flex; gap: 12px; }
    .btn-primary {
      background: #409eff;
      color: #fff;
      border: none;
      padding: 10px 20px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }
    .btn-primary:hover { background: #66b1ff; transform: translateY(-1px); }
    .btn-secondary {
      background: #fff;
      color: #606266;
      border: 1px solid #dcdfe6;
      padding: 10px 20px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }
    .btn-secondary:hover { border-color: #409eff; color: #409eff; }
    .filter-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    .filter-row {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
      align-items: center;
    }
    .filter-item {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .filter-label { font-size: 14px; color: #606266; white-space: nowrap; }
    .filter-select {
      padding: 8px 32px 8px 12px;
      border: 1px solid #dcdfe6;
      border-radius: 6px;
      font-size: 14px;
      min-width: 140px;
      background: #fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23606060' d='M2 4l4 4 4-4'/%3E%3C/svg%3E") no-repeat right 10px center;
      cursor: pointer;
      appearance: none;
    }
    .filter-select:focus { outline: none; border-color: #409eff; }
    .search-input {
      padding: 8px 12px 8px 36px;
      border: 1px solid #dcdfe6;
      border-radius: 6px;
      font-size: 14px;
      width: 240px;
      background: #fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23909090' stroke-width='2'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cpath d='m21 21-4.35-4.35'/%3E%3C/svg%3E") no-repeat left 10px center;
    }
    .search-input:focus { outline: none; border-color: #409eff; }
    .filter-stats {
      margin-left: auto;
      font-size: 13px;
      color: #909399;
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .stat-item { display: flex; align-items: center; gap: 4px; }
    .stat-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }
    .stat-dot.es { background: #67c23a; }
    .stat-dot.vector { background: #e6a23c; }
    .stat-dot.graph { background: #909eff; }
    .knowledge-table {
      background: #fff;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    .table-header {
      display: grid;
      grid-template-columns: 2fr 100px 100px 200px 120px;
      padding: 14px 20px;
      background: #f5f7fa;
      font-size: 13px;
      font-weight: 600;
      color: #606266;
      border-bottom: 1px solid #ebeef5;
    }
    .table-row {
      display: grid;
      grid-template-columns: 2fr 100px 100px 200px 120px;
      padding: 16px 20px;
      align-items: center;
      border-bottom: 1px solid #f0f0f0;
      transition: all 0.15s;
    }
    .table-row:hover { background: #f8fafc; }
    .table-row:last-child { border-bottom: none; }
    .knowledge-info { display: flex; flex-direction: column; gap: 4px; }
    .knowledge-title {
      font-size: 14px;
      font-weight: 500;
      color: #303133;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .knowledge-title:hover { color: #409eff; }
    .type-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 500;
    }
    .type-file { background: #e8f4fd; color: #1890ff; }
    .type-text { background: #fef0e8; color: #ff6a00; }
    .type-url { background: #e8f8f0; color: #52c41a; }
    .knowledge-meta { font-size: 12px; color: #909399; display: flex; align-items: center; gap: 8px; }
    .category-tag {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 12px;
    }
    .cat-law { background: #fde2e2; color: #cf4444; }
    .cat-tech { background: #e8f9e8; color: #389b48; }
    .cat-case { background: #fff3e0; color: #d9822b; }
    .cat-policy { background: #e8eaf6; color: #4f5bd5; }
    .status-group { display: flex; gap: 8px; flex-wrap: wrap; }
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }
    .status-badge svg { width: 14px; height: 14px; }
    .status-es {
      background: #f0f9eb;
      color: #67c23a;
      border: 1px solid #c2e7b0;
    }
    .status-es:hover { background: #d4edbc; }
    .status-es.pending {
      background: #fdf6ec;
      color: #e6a23c;
      border: 1px solid #f5dab1;
    }
    .status-vector {
      background: #ecf5ff;
      color: #409eff;
      border: 1px solid #b3d8fd;
    }
    .status-vector:hover { background: #c2e1ff; }
    .status-vector.pending {
      background: #fdf6ec;
      color: #e6a23c;
      border: 1px solid #f5dab1;
    }
    .status-graph {
      background: #f4f3ff;
      color: #909eff;
      border: 1px solid #d3d4f1;
    }
    .status-graph:hover { background: #c5c6ef; }
    .status-graph.pending {
      background: #fdf6ec;
      color: #e6a23c;
      border: 1px solid #f5dab1;
    }
    .status-action-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 6px;
      border: none;
      cursor: pointer;
      transition: all 0.2s;
      margin: 0 2px;
    }
    .status-action-btn:hover { transform: scale(1.1); }
    .status-action-btn.es { background: #f0f9eb; color: #67c23a; }
    .status-action-btn.es:hover { background: #67c23a; color: #fff; }
    .status-action-btn.vector { background: #ecf5ff; color: #409eff; }
    .status-action-btn.vector:hover { background: #409eff; color: #fff; }
    .status-action-btn.graph { background: #f4f3ff; color: #909eff; }
    .status-action-btn.graph:hover { background: #909eff; color: #fff; }
    .status-action-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
    .status-action-btn:disabled:hover { transform: none; }
    .op-btn {
      padding: 6px 12px;
      border-radius: 4px;
      font-size: 13px;
      cursor: pointer;
      transition: all 0.15s;
      border: none;
      background: transparent;
    }
    .op-btn.view {
      color: #409eff;
      background: #ecf5ff;
    }
    .op-btn.view:hover { background: #c2e1ff; }
    .op-btn.edit {
      color: #67c23a;
      background: #f0f9eb;
    }
    .op-btn.edit:hover { background: #c2e7b0; }
    .op-btn.more {
      color: #909399;
      background: #f5f5f5;
    }
    .op-btn.more:hover { background: #e8e8e8; }
    .pagination {
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 20px;
      gap: 8px;
    }
    .page-btn {
      min-width: 36px;
      height: 36px;
      border: 1px solid #dcdfe6;
      background: #fff;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      color: #606266;
      transition: all 0.15s;
    }
    .page-btn:hover:not(:disabled) { border-color: #409eff; color: #409eff; }
    .page-btn.active { background: #409eff; color: #fff; border-color: #409eff; }
    .page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .dialog-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    .dialog {
      background: #fff;
      border-radius: 12px;
      width: 90%;
      max-width: 600px;
      max-height: 90vh;
      overflow: hidden;
      animation: slideUp 0.2s ease;
    }
    @keyframes slideUp {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .dialog-header {
      padding: 20px 24px;
      border-bottom: 1px solid #ebeef5;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .dialog-title { font-size: 18px; font-weight: 600; color: #303133; }
    .dialog-close {
      width: 32px;
      height: 32px;
      border: none;
      background: transparent;
      cursor: pointer;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #909399;
      transition: all 0.15s;
    }
    .dialog-close:hover { background: #f5f5f5; }
    .dialog-body { padding: 24px; max-height: 60vh; overflow-y: auto; }
    .form-item { margin-bottom: 20px; }
    .form-label {
      display: block;
      font-size: 14px;
      color: #606266;
      margin-bottom: 8px;
      font-weight: 500;
    }
    .form-label.required::before { content: '*'; color: #f56c6c; margin-right: 4px; }
    .form-input {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #dcdfe6;
      border-radius: 6px;
      font-size: 14px;
      transition: all 0.15s;
    }
    .form-input:focus { outline: none; border-color: #409eff; box-shadow: 0 0 0 2px rgba(64,158,255,0.1); }
    .form-select {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #dcdfe6;
      border-radius: 6px;
      font-size: 14px;
      background: #fff;
      cursor: pointer;
    }
    .dialog-footer {
      padding: 16px 24px;
      border-top: 1px solid #ebeef5;
      display: flex;
      justify-content: flex-end;
      gap: 12px;
    }
    .btn-cancel {
      padding: 10px 20px;
      border: 1px solid #dcdfe6;
      background: #fff;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      color: #606266;
      transition: all 0.15s;
    }
    .btn-cancel:hover { border-color: #409eff; color: #409eff; }
    .btn-confirm {
      padding: 10px 24px;
      border: none;
      background: #409eff;
      color: #fff;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.15s;
    }
    .btn-confirm:hover { background: #66b1ff; }
    .btn-confirm:disabled { opacity: 0.6; cursor: not-allowed; }
    .upload-zone {
      border: 2px dashed #dcdfe6;
      border-radius: 8px;
      padding: 40px;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s;
    }
    .upload-zone:hover { border-color: #409eff; background: #f8fafc; }
    .upload-icon { font-size: 48px; color: #c0c4cc; margin-bottom: 12px; }
    .upload-text { color: #606266; font-size: 14px; }
    .upload-text em { color: #409eff; font-style: normal; }
    .upload-hint { color: #909399; font-size: 12px; margin-top: 8px; }
    .editor-toolbar {
      display: flex;
      gap: 8px;
      padding: 8px;
      background: #f5f7fa;
      border-radius: 6px 6px 0 0;
      border: 1px solid #dcdfe6;
      border-bottom: none;
    }
    .toolbar-btn {
      width: 32px;
      height: 32px;
      border: none;
      background: transparent;
      border-radius: 4px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #606266;
      transition: all 0.15s;
    }
    .toolbar-btn:hover { background: #fff; color: #409eff; }
    .toolbar-btn.active { background: #409eff; color: #fff; }
    .editor-content {
      min-height: 200px;
      padding: 12px;
      border: 1px solid #dcdfe6;
      border-radius: 0 0 6px 6px;
      font-size: 14px;
      line-height: 1.6;
    }
    .editor-content:focus { outline: none; border-color: #409eff; }
    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: #909399;
    }
    .empty-icon { font-size: 64px; margin-bottom: 16px; opacity: 0.5; }
    .empty-text { font-size: 14px; }
    .context-menu {
      position: fixed;
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.15);
      padding: 6px 0;
      min-width: 160px;
      z-index: 1001;
    }
    .context-item {
      padding: 10px 16px;
      font-size: 14px;
      color: #303133;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all 0.15s;
    }
    .context-item:hover { background: #f5f7fa; }
    .context-item.danger { color: #f56c6c; }
    .context-item.danger:hover { background: #fef0f0; }
    .toast {
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      padding: 12px 24px;
      background: #303133;
      color: #fff;
      border-radius: 8px;
      font-size: 14px;
      z-index: 2000;
      animation: fadeInUp 0.3s ease;
    }
    @keyframes fadeInUp {
      from { opacity: 0; transform: translate(-50%, 10px); }
      to { opacity: 1; transform: translate(-50%, 0); }
    }
    .toast.success { background: #67c23a; }
    .toast.error { background: #f56c6c; }
    .detail-panel {
      position: fixed;
      top: 0;
      right: 0;
      width: 500px;
      height: 100vh;
      background: #fff;
      box-shadow: -4px 0 20px rgba(0,0,0,0.1);
      z-index: 1000;
      animation: slideIn 0.25s ease;
      display: flex;
      flex-direction: column;
    }
    @keyframes slideIn {
      from { transform: translateX(100%); }
      to { transform: translateX(0); }
    }
    .panel-header {
      padding: 20px 24px;
      border-bottom: 1px solid #ebeef5;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }
    .panel-title { font-size: 18px; font-weight: 600; color: #303133; flex: 1; }
    .panel-body { flex: 1; overflow-y: auto; padding: 24px; }
    .detail-section { margin-bottom: 24px; }
    .detail-label { font-size: 12px; color: #909399; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
    .detail-value { font-size: 14px; color: #303133; }
    .detail-tags { display: flex; gap: 6px; flex-wrap: wrap; }
    .detail-tag { padding: 4px 10px; background: #f0f2f5; border-radius: 4px; font-size: 12px; color: #606266; }
    .status-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
    .status-card {
      padding: 16px;
      border-radius: 8px;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s;
    }
    .status-card.es { background: #f0f9eb; border: 1px solid #e1f3d8; }
    .status-card.es:hover { background: #d4edbc; }
    .status-card.vector { background: #ecf5ff; border: 1px solid #d9ecff; }
    .status-card.vector:hover { background: #c2e1ff; }
    .status-card.graph { background: #f4f3ff; border: 1px solid #e4e6f0; }
    .status-card.graph:hover { background: #c5c6ef; }
    .status-card-icon { font-size: 24px; margin-bottom: 8px; }
    .status-card-label { font-size: 13px; font-weight: 500; }
    .status-card-value { font-size: 20px; font-weight: 600; margin-top: 4px; }
    .action-log { background: #f8fafc; border-radius: 8px; padding: 16px; }
    .log-item {
      display: flex;
      gap: 12px;
      padding: 10px 0;
      border-bottom: 1px solid #ebeef5;
      font-size: 13px;
    }
    .log-item:last-child { border-bottom: none; }
    .log-time { color: #909399; min-width: 140px; }
    .log-action { color: #303133; flex: 1; }
    .log-user { color: #409eff; }
  </style>
</head>
<body>
  <div id="app">
    <div class="app-container">
      <!-- 侧边栏 -->
      <div class="sidebar">
        <div class="logo">
          <h1>知识中心</h1>
          <span>Knowledge Center</span>
        </div>
        <div class="nav-item active">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
          知识管理
        </div>
        <div class="nav-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
          知识问答
        </div>
        <div class="nav-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
          图谱浏览
        </div>
        <div class="nav-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
          文档库
        </div>
        <div class="nav-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
          系统设置
        </div>
      </div>

      <!-- 主内容区 -->
      <div class="main-content">
        <div class="page-header">
          <h1 class="page-title">知识管理</h1>
          <div class="header-actions">
            <button class="btn-primary" @click="showUploadDialog = true">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
              上传知识
            </button>
            <button class="btn-secondary" @click="showTextDialog = true">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
              手动添加
            </button>
          </div>
        </div>

        <!-- 筛选区域 -->
        <div class="filter-card">
          <div class="filter-row">
            <div class="filter-item">
              <span class="filter-label">知识类型</span>
              <select class="filter-select" v-model="filters.type" @change="handleFilter">
                <option value="">全部</option>
                <option value="file">文件</option>
                <option value="text">富文本</option>
                <option value="url">链接</option>
              </select>
            </div>
            <div class="filter-item">
              <span class="filter-label">知识分类</span>
              <select class="filter-select" v-model="filters.category" @change="handleFilter">
                <option value="">全部分类</option>
                <option value="law">法律法规</option>
                <option value="tech">技术标准</option>
                <option value="case">执法案例</option>
                <option value="policy">政策文件</option>
              </select>
            </div>
            <div class="filter-item">
              <span class="filter-label">ES状态</span>
              <select class="filter-select" v-model="filters.esStatus" @change="handleFilter">
                <option value="">全部</option>
                <option value="indexed">已存储</option>
                <option value="pending">待处理</option>
                <option value="failed">失败</option>
              </select>
            </div>
            <div class="filter-item">
              <span class="filter-label">向量化</span>
              <select class="filter-select" v-model="filters.vectorStatus" @change="handleFilter">
                <option value="">全部</option>
                <option value="done">已完成</option>
                <option value="pending">待处理</option>
                <option value="failed">失败</option>
              </select>
            </div>
            <div class="filter-item">
              <span class="filter-label">图库</span>
              <select class="filter-select" v-model="filters.graphStatus" @change="handleFilter">
                <option value="">全部</option>
                <option value="done">已入图库</option>
                <option value="pending">待处理</option>
                <option value="failed">失败</option>
              </select>
            </div>
            <input type="text" class="search-input" placeholder="搜索标题..." v-model="filters.keyword" @keyup.enter="handleFilter">
            <button class="btn-secondary" @click="resetFilter" style="padding: 8px 16px;">重置</button>
            <div class="filter-stats">
              <span class="stat-item"><span class="stat-dot es"></span>ES {{ stats.esIndexed }}/{{ stats.total }}</span>
              <span class="stat-item"><span class="stat-dot vector"></span>向量化 {{ stats.vectorDone }}/{{ stats.total }}</span>
              <span class="stat-item"><span class="stat-dot graph"></span>图库 {{ stats.graphDone }}/{{ stats.total }}</span>
            </div>
          </div>
        </div>

        <!-- 知识列表 -->
        <div class="knowledge-table">
          <div class="table-header">
            <div>知识内容</div>
            <div>类型</div>
            <div>分类</div>
            <div>状态</div>
            <div>操作</div>
          </div>
          <div class="table-body">
            <div class="table-row" v-for="item in knowledgeList" :key="item.id" @click="openDetail(item)">
              <div class="knowledge-info">
                <div class="knowledge-title">
                  <span :class="'type-badge type-' + item.type">
                    <svg v-if="item.type === 'file'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                    <svg v-else-if="item.type === 'text'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                    <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                    {{ item.typeName }}
                  </span>
                  {{ item.title }}
                </div>
                <div class="knowledge-meta">
                  <span>{{ item.source || '无来源' }}</span>
                  <span>•</span>
                  <span>{{ item.size }}</span>
                  <span>•</span>
                  <span>{{ item.createdAt }}</span>
                </div>
              </div>
              <div>
                <span :class="'category-tag cat-' + item.category">{{ item.categoryName }}</span>
              </div>
              <div class="status-group">
                <!-- ES 状态 -->
                <div style="display: flex; align-items: center; gap: 4px;">
                  <span :class="'status-badge status-es ' + (item.esStatus === 'pending' ? 'pending' : '')"
                        :title="item.esStatus === 'indexed' ? '已存储至ES' : '待处理'">
                    <svg v-if="item.esStatus === 'indexed'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                    ES
                  </span>
                  <button class="status-action-btn es"
                          @click.stop="retryProcess(item, 'es')"
                          title="重新索引">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
                  </button>
                </div>
                <!-- 向量 状态 -->
                <div style="display: flex; align-items: center; gap: 4px;">
                  <span :class="'status-badge status-vector ' + (item.vectorStatus === 'pending' ? 'pending' : '')"
                        :title="item.vectorStatus === 'done' ? '已完成向量化' : '待处理'">
                    <svg v-if="item.vectorStatus === 'done'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                    矢量
                  </span>
                  <button class="status-action-btn vector"
                          @click.stop="retryProcess(item, 'vector')"
                          :disabled="item.vectorStatus === 'done'"
                          title="重新向量化">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
                  </button>
                </div>
                <!-- 图谱 状态 -->
                <div style="display: flex; align-items: center; gap: 4px;">
                  <span :class="'status-badge status-graph ' + (item.graphStatus === 'pending' ? 'pending' : '')"
                        :title="item.graphStatus === 'done' ? '已入图库' : '待处理'">
                    <svg v-if="item.graphStatus === 'done'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                    图谱
                  </span>
                  <button class="status-action-btn graph"
                          @click.stop="retryProcess(item, 'graph')"
                          :disabled="item.graphStatus === 'done'"
                          title="重新入库">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
                  </button>
                </div>
              </div>
              <div class="op-btns" @click.stop>
                <button class="op-btn view" @click="openDetail(item)">查看</button>
                <button class="op-btn more" @click="showContextMenu($event, item)">更多</button>
              </div>
            </div>
            <div class="empty-state" v-if="knowledgeList.length === 0">
              <div class="empty-icon">📭</div>
              <div class="empty-text">暂无知识内容</div>
            </div>
          </div>
          <div class="pagination">
            <button class="page-btn" :disabled="pagination.page <= 1" @click="pagination.page--; loadData()">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"></polyline></svg>
            </button>
            <button class="page-btn" v-for="p in visiblePages" :key="p"
                    :class="{ active: p === pagination.page }"
                    @click="pagination.page = p; loadData()">{{ p }}</button>
            <button class="page-btn" :disabled="pagination.page >= pagination.total" @click="pagination.page++; loadData()">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传对话框 -->
    <div class="dialog-overlay" v-if="showUploadDialog" @click.self="showUploadDialog = false">
      <div class="dialog">
        <div class="dialog-header">
          <h3 class="dialog-title">上传知识文件</h3>
          <button class="dialog-close" @click="showUploadDialog = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-item">
            <label class="form-label required">上传文件</label>
            <div class="upload-zone" @click="$refs.fileInput.click()">
              <div class="upload-icon">📄</div>
              <div class="upload-text">将文件拖到此处，或<em>点击上传</em></div>
              <div class="upload-hint">支持 PDF、Word、TXT 格式，大小不超过 50MB</div>
            </div>
            <input type="file" ref="fileInput" style="display:none" accept=".pdf,.doc,.docx,.txt" @change="handleFileSelect">
          </div>
          <div class="form-item">
            <label class="form-label">标题</label>
            <input type="text" class="form-input" v-model="uploadForm.title" placeholder="不填则使用文件名">
          </div>
          <div class="form-item">
            <label class="form-label required">知识分类</label>
            <select class="form-select" v-model="uploadForm.category">
              <option value="">请选择分类</option>
              <option value="law">法律法规</option>
              <option value="tech">技术标准</option>
              <option value="case">执法案例</option>
              <option value="policy">政策文件</option>
            </select>
          </div>
          <div class="form-item">
            <label class="form-label">来源</label>
            <input type="text" class="form-input" v-model="uploadForm.source" placeholder="如：国务院令第279号">
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showUploadDialog = false">取消</button>
          <button class="btn-confirm" @click="handleUpload" :disabled="!uploadForm.file || !uploadForm.category">上传</button>
        </div>
      </div>
    </div>

    <!-- 手动添加对话框 -->
    <div class="dialog-overlay" v-if="showTextDialog" @click.self="showTextDialog = false">
      <div class="dialog" style="max-width: 700px;">
        <div class="dialog-header">
          <h3 class="dialog-title">添加富文本知识</h3>
          <button class="dialog-close" @click="showTextDialog = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-item">
            <label class="form-label required">标题</label>
            <input type="text" class="form-input" v-model="textForm.title" placeholder="请输入知识标题">
          </div>
          <div class="form-item">
            <label class="form-label required">内容</label>
            <div class="editor-toolbar">
              <button class="toolbar-btn" :class="{ active: textForm.bold }" @click="textForm.bold = !textForm.bold" title="粗体"><strong>B</strong></button>
              <button class="toolbar-btn" :class="{ active: textForm.italic }" @click="textForm.italic = !textForm.italic" title="斜体"><em>I</em></button>
              <button class="toolbar-btn" @click="textForm.list = !textForm.list" title="列表" :class="{ active: textForm.list }">☰</button>
            </div>
            <div class="editor-content" contenteditable="true" @input="textForm.content = $event.target.innerHTML"
                 style="white-space: pre-wrap;" placeholder="请输入知识内容..."></div>
          </div>
          <div class="form-item">
            <label class="form-label required">知识分类</label>
            <select class="form-select" v-model="textForm.category">
              <option value="">请选择分类</option>
              <option value="law">法律法规</option>
              <option value="tech">技术标准</option>
              <option value="case">执法案例</option>
              <option value="policy">政策文件</option>
            </select>
          </div>
          <div class="form-item">
            <label class="form-label">来源</label>
            <input type="text" class="form-input" v-model="textForm.source" placeholder="如：国务院令第279号">
          </div>
          <div class="form-item">
            <label class="form-label">标签</label>
            <input type="text" class="form-input" v-model="textForm.tags" placeholder="多个标签用逗号分隔">
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showTextDialog = false">取消</button>
          <button class="btn-confirm" @click="handleTextSubmit" :disabled="!textForm.title || !textForm.content || !textForm.category">保存</button>
        </div>
      </div>
    </div>

    <!-- 详情面板 -->
    <div class="detail-panel" v-if="showDetailPanel">
      <div class="panel-header">
        <h3 class="panel-title">{{ currentItem.title }}</h3>
        <button class="dialog-close" @click="showDetailPanel = false">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
      <div class="panel-body">
        <div class="detail-section">
          <div class="detail-label">基本信息</div>
          <div class="detail-value" style="display: flex; gap: 8px; margin-bottom: 12px;">
            <span :class="'type-badge type-' + currentItem.type">{{ currentItem.typeName }}</span>
            <span :class="'category-tag cat-' + currentItem.category">{{ currentItem.categoryName }}</span>
          </div>
          <p style="font-size: 14px; color: #606266; line-height: 1.6;">{{ currentItem.description || '暂无描述' }}</p>
        </div>
        <div class="detail-section">
          <div class="detail-label">处理状态</div>
          <div class="status-grid">
            <div class="status-card es" @click="retryProcess('es')">
              <div class="status-card-icon">🔍</div>
              <div class="status-card-label">ES 存储</div>
              <div class="status-card-value" :style="{ color: currentItem.esStatus === 'indexed' ? '#67c23a' : '#e6a23c' }">
                {{ currentItem.esStatus === 'indexed' ? '已存储' : '待处理' }}
              </div>
            </div>
            <div class="status-card vector" @click="retryProcess('vector')">
              <div class="status-card-icon">📐</div>
              <div class="status-card-label">向量化</div>
              <div class="status-card-value" :style="{ color: currentItem.vectorStatus === 'done' ? '#67c23a' : '#e6a23c' }">
                {{ currentItem.vectorStatus === 'done' ? '已完成' : '待处理' }}
              </div>
            </div>
            <div class="status-card graph" @click="retryProcess('graph')">
              <div class="status-card-icon">🕸️</div>
              <div class="status-card-label">图谱入库</div>
              <div class="status-card-value" :style="{ color: currentItem.graphStatus === 'done' ? '#67c23a' : '#e6a23c' }">
                {{ currentItem.graphStatus === 'done' ? '已入图库' : '待处理' }}
              </div>
            </div>
          </div>
        </div>
        <div class="detail-section">
          <div class="detail-label">元数据</div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div>
              <div class="detail-label" style="font-size: 11px;">来源</div>
              <div class="detail-value">{{ currentItem.source || '-' }}</div>
            </div>
            <div>
              <div class="detail-label" style="font-size: 11px;">大小</div>
              <div class="detail-value">{{ currentItem.size }}</div>
            </div>
            <div>
              <div class="detail-label" style="font-size: 11px;">创建时间</div>
              <div class="detail-value">{{ currentItem.createdAt }}</div>
            </div>
            <div>
              <div class="detail-label" style="font-size: 11px;">更新时间</div>
              <div class="detail-value">{{ currentItem.updatedAt }}</div>
            </div>
          </div>
        </div>
        <div class="detail-section" v-if="currentItem.tags && currentItem.tags.length">
          <div class="detail-label">标签</div>
          <div class="detail-tags">
            <span class="detail-tag" v-for="tag in currentItem.tags" :key="tag">{{ tag }}</span>
          </div>
        </div>
        <div class="detail-section">
          <div class="detail-label">操作日志</div>
          <div class="action-log">
            <div class="log-item" v-for="log in currentItem.logs" :key="log.time">
              <span class="log-time">{{ log.time }}</span>
              <span class="log-action">{{ log.action }}</span>
              <span class="log-user">{{ log.user }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右键菜单 -->
    <div class="context-menu" v-if="contextMenu.show" :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }">
      <div class="context-item" @click="openDetail(contextMenu.item); contextMenu.show = false">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
        查看详情
      </div>
      <div class="context-item" @click="contextMenu.show = false">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
        编辑
      </div>
      <div class="context-item" @click="reprocessItem(contextMenu.item); contextMenu.show = false">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
        重新处理
      </div>
      <div class="context-item" @click="contextMenu.show = false">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
        复制链接
      </div>
      <div style="border-top: 1px solid #ebeef5; margin: 6px 0;"></div>
      <div class="context-item danger" @click="deleteItem(contextMenu.item); contextMenu.show = false">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
        删除
      </div>
    </div>

    <!-- Toast -->
    <div class="toast" :class="toast.type" v-if="toast.show">{{ toast.message }}</div>
  </div>

  <script>
    const { createApp, ref, reactive, computed, onMounted } = Vue

    createApp({
      setup() {
        const knowledgeList = ref([])
        const showUploadDialog = ref(false)
        const showTextDialog = ref(false)
        const showDetailPanel = ref(false)
        const currentItem = ref({})

        const filters = reactive({
          type: '',
          category: '',
          esStatus: '',
          vectorStatus: '',
          graphStatus: '',
          keyword: ''
        })

        const pagination = reactive({
          page: 1,
          pageSize: 10,
          total: 10
        })

        const stats = reactive({
          total: 12,
          esIndexed: 10,
          vectorDone: 8,
          graphDone: 6
        })

        const uploadForm = reactive({
          file: null,
          title: '',
          category: '',
          source: ''
        })

        const textForm = reactive({
          title: '',
          content: '',
          category: '',
          source: '',
          tags: '',
          bold: false,
          italic: false,
          list: false
        })

        const contextMenu = reactive({
          show: false,
          x: 0,
          y: 0,
          item: null
        })

        const toast = reactive({
          show: false,
          message: '',
          type: 'success'
        })

        const visiblePages = computed(() => {
          const pages = []
          const total = pagination.total
          const current = pagination.page
          let start = Math.max(1, current - 2)
          let end = Math.min(total, start + 4)
          if (end - start < 4) start = Math.max(1, end - 4)
          for (let i = start; i <= end; i++) pages.push(i)
          return pages
        })

        const showToast = (message, type = 'success') => {
          toast.message = message
          toast.type = type
          toast.show = true
          setTimeout(() => toast.show = false, 3000)
        }

        const loadData = () => {
          // 模拟数据
          knowledgeList.value = [
            { id: 1, title: '中华人民共和国安全生产法', type: 'file', typeName: '文件', category: 'law', categoryName: '法律法规', source: '国务院令第88号', size: '2.5MB', createdAt: '2024-03-15 10:30', updatedAt: '2024-03-15 14:20', esStatus: 'indexed', vectorStatus: 'done', graphStatus: 'done', description: '安全生产法是我国安全生产领域的基本法律...', tags: ['安全生产', '法律'], logs: [{ time: '2024-03-15 14:20', action: '更新状态', user: '系统' }, { time: '2024-03-15 10:30', action: '创建知识', user: '张三' }] },
            { id: 2, title: '危险化学品储存安全规范', type: 'file', typeName: '文件', category: 'tech', categoryName: '技术标准', source: 'GB/T 12345-2020', size: '1.8MB', createdAt: '2024-03-14 09:15', updatedAt: '2024-03-14 16:45', esStatus: 'indexed', vectorStatus: 'done', graphStatus: 'pending', description: '规定了危险化学品储存的基本要求...', tags: ['危化品', '储存', '标准'], logs: [{ time: '2024-03-14 16:45', action: '向量化完成', user: '系统' }] },
            { id: 3, title: '2024年安全生产月活动方案', type: 'text', typeName: '富文本', category: 'policy', categoryName: '政策文件', source: '应急管理部', size: '-', createdAt: '2024-03-13 14:20', updatedAt: '2024-03-13 14:20', esStatus: 'pending', vectorStatus: 'pending', graphStatus: 'pending', description: '关于开展2024年安全生产月活动的通知...', tags: ['安全生产月', '活动'], logs: [] },
            { id: 4, title: '某化工企业火灾事故调查报告', type: 'text', typeName: '富文本', category: 'case', categoryName: '执法案例', source: '应急管理部公告', size: '-', createdAt: '2024-03-12 11:00', updatedAt: '2024-03-12 11:00', esStatus: 'indexed', vectorStatus: 'done', graphStatus: 'done', description: '2024年1月，某化工企业发生火灾...', tags: ['火灾', '事故', '调查'], logs: [{ time: '2024-03-12 15:30', action: '入图库', user: '系统' }] },
            { id: 5, title: '特种设备安全监察条例', type: 'url', typeName: '链接', category: 'law', categoryName: '法律法规', source: '国务院令第549号', size: '-', createdAt: '2024-03-11 08:45', updatedAt: '2024-03-11 08:45', esStatus: 'indexed', vectorStatus: 'done', graphStatus: 'done', description: '特种设备安全监察条例全文...', tags: ['特种设备', '监察'], logs: [] },
            { id: 6, title: '粉尘防爆安全规程', type: 'file', typeName: '文件', category: 'tech', categoryName: '技术标准', source: 'GB 15577-2018', size: '3.2MB', createdAt: '2024-03-10 16:30', updatedAt: '2024-03-10 16:30', esStatus: 'indexed', vectorStatus: 'pending', graphStatus: 'pending', description: '适用于粉尘爆炸危险场所的防爆安全要求...', tags: ['粉尘', '防爆', '标准'], logs: [] },
          ]
        }

        const handleFilter = () => {
          pagination.page = 1
          loadData()
        }

        const resetFilter = () => {
          filters.type = ''
          filters.category = ''
          filters.esStatus = ''
          filters.vectorStatus = ''
          filters.graphStatus = ''
          filters.keyword = ''
          handleFilter()
        }

        const handleFileSelect = (e) => {
          const file = e.target.files[0]
          if (file) {
            uploadForm.file = file
            if (!uploadForm.title) {
              uploadForm.title = file.name.replace(/\.[^.]+$/, '')
            }
          }
        }

        const handleUpload = () => {
          if (!uploadForm.file || !uploadForm.category) return
          showToast('文件上传成功！')
          showUploadDialog.value = false
          uploadForm.file = null
          uploadForm.title = ''
          uploadForm.category = ''
          uploadForm.source = ''
          loadData()
        }

        const handleTextSubmit = () => {
          if (!textForm.title || !textForm.content || !textForm.category) return
          showToast('知识添加成功！')
          showTextDialog.value = false
          textForm.title = ''
          textForm.content = ''
          textForm.category = ''
          textForm.source = ''
          textForm.tags = ''
          loadData()
        }

        const openDetail = (item) => {
          currentItem.value = item
          showDetailPanel.value = true
          contextMenu.show = false
        }

        const toggleStatus = (item, type) => {
          showToast(`已触发${type === 'es' ? 'ES索引' : type === 'vector' ? '向量化' : '图谱入库'}处理`)
        }

        const retryProcess = (type) => {
          showToast(`已提交${type === 'es' ? 'ES索引' : type === 'vector' ? '向量化' : '图谱入库'}任务`)
        }

        const showContextMenu = (e, item) => {
          contextMenu.x = e.clientX
          contextMenu.y = e.clientY
          contextMenu.item = item
          contextMenu.show = true
        }

        const reprocessItem = (item) => {
          showToast('已提交重新处理任务')
        }

        const deleteItem = (item) => {
          showToast('删除成功', 'success')
        }

        onMounted(() => {
          loadData()
          document.addEventListener('click', () => {
            contextMenu.show = false
          })
        })

        return {
          knowledgeList,
          showUploadDialog,
          showTextDialog,
          showDetailPanel,
          currentItem,
          filters,
          pagination,
          stats,
          uploadForm,
          textForm,
          contextMenu,
          toast,
          visiblePages,
          loadData,
          handleFilter,
          resetFilter,
          handleFileSelect,
          handleUpload,
          handleTextSubmit,
          openDetail,
          toggleStatus,
          retryProcess,
          showContextMenu,
          reprocessItem,
          deleteItem,
          showToast
        }
      }
    }).mount('#app')
  </script>
</body>
</html>