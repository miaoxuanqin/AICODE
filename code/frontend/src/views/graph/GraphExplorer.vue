<template>
  <div class="graph-explorer-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>知识图谱
        <el-tag type="warning" size="small">Graph Explorer</el-tag>
        <el-tag v-if="graphStats.available" type="success" size="small">
          {{ graphStats.total_nodes }} 节点 / {{ graphStats.total_edges }} 关系
        </el-tag>
        <el-tag v-else type="danger" size="small">离线</el-tag>
      </h2>
      <p class="subtitle">探索知识实体间的关联关系，发现隐藏的知识脉络</p>
    </div>

    <el-row :gutter="24">
      <!-- 左侧：图谱画布 -->
      <el-col :span="18">
        <el-card class="graph-card">
          <template #header>
            <div class="graph-header">
              <span>图谱可视化</span>
              <div class="graph-controls">
                <el-button size="small" @click="resetView" title="重置视图">
                  <el-icon><RefreshRight /></el-icon>
                </el-button>
                <el-button size="small" @click="fitView" title="适应画布">
                  <el-icon><FullScreen /></el-icon>
                </el-button>
                <el-button size="small" @click="showPathExplorer = true" title="路径探索">
                  <el-icon><Guide /></el-icon>
                </el-button>
              </div>
            </div>
          </template>

          <!-- 图谱容器 -->
          <div class="graph-container" ref="graphContainer">
            <!-- 图例 -->
            <div class="graph-legend">
              <div v-for="type in nodeTypes" :key="type.label" class="legend-item" @click="toggleTypeFilter(type.label)">
                <span class="legend-dot" :style="{ background: type.color }"></span>
                <span>{{ type.name }}</span>
                <span class="legend-count">({{ graphStats.by_type?.[type.label] || 0 }})</span>
              </div>
            </div>

            <!-- 加载状态 -->
            <div v-if="loading" class="graph-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>正在加载图谱...</span>
            </div>

            <!-- 图谱画布 -->
            <div ref="networkRef" class="network-canvas"></div>

            <!-- 空状态 -->
            <div v-if="!loading && nodes.length === 0 && !graphStats.available" class="graph-empty">
              <el-icon :size="64"><Connection /></el-icon>
              <p>图谱服务暂不可用</p>
              <p class="hint">请检查 Neo4j 服务是否正常运行</p>
            </div>

            <div v-if="!loading && nodes.length === 0 && graphStats.available" class="graph-empty">
              <el-icon :size="64"><Box /></el-icon>
              <p>暂无图谱数据</p>
              <p class="hint">请先上传知识文档，系统将自动抽取实体关系</p>
            </div>
          </div>

          <!-- 搜索工具栏 -->
          <div class="search-toolbar">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索实体名称..."
              clearable
              @keyup.enter="handleSearch"
              style="width: 300px;"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="typeFilter"
              multiple
              collapse-tags
              collapse-tags-tooltip
              placeholder="按类型筛选"
              style="width: 200px; margin-left: 12px;"
              @change="handleTypeFilterChange"
            >
              <el-option
                v-for="type in nodeTypes"
                :key="type.label"
                :label="type.name"
                :value="type.label"
              />
            </el-select>
            <el-button @click="clearFilters" style="margin-left: 12px;">重置</el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：节点详情 & 统计 -->
      <el-col :span="6">
        <!-- 节点详情面板 -->
        <el-card class="detail-card" v-if="selectedNode">
          <template #header>
            <div class="detail-header">
              <span>节点详情</span>
              <el-button text @click="selectedNode = null">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="node-detail">
            <div class="node-type-tag" :style="{ background: getNodeColor(selectedNode.label) }">
              {{ getNodeTypeName(selectedNode.label) }}
            </div>
            <div class="node-name">{{ selectedNode.name }}</div>

            <div class="detail-section">
              <div class="section-title">关联关系</div>
              <div v-if="nodeRelations.length > 0" class="relations-list">
                <div
                  v-for="rel in nodeRelations"
                  :key="rel.id"
                  class="relation-item"
                  @click="handleRelationClick(rel)"
                >
                  <span class="rel-type">{{ getRelationName(rel.type) }}</span>
                  <span class="rel-arrow">{{ rel.direction === 'outgoing' ? '→' : '←' }}</span>
                  <span class="rel-target">{{ rel.direction === 'outgoing' ? rel.target_name : rel.source_name }}</span>
                </div>
              </div>
              <div v-else class="empty-relations">暂无关联关系</div>
            </div>

            <div class="detail-actions">
              <el-button type="primary" size="small" @click="expandNode(selectedNode.name)">
                <el-icon><Plus /></el-icon>
                展开邻居
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 统计面板 -->
        <el-card class="stats-card">
          <template #header>
            <span>图谱统计</span>
          </template>
          <div class="stats-content">
            <div class="stat-item">
              <div class="stat-value">{{ graphStats.total_nodes || 0 }}</div>
              <div class="stat-label">总节点数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ graphStats.total_edges || 0 }}</div>
              <div class="stat-label">总关系数</div>
            </div>
          </div>

          <div class="type-distribution" v-if="Object.keys(graphStats.by_type || {}).length > 0">
            <div class="section-title">类型分布</div>
            <div class="type-bars">
              <div
                v-for="type in nodeTypes"
                :key="type.label"
                class="type-bar-item"
              >
                <span class="type-name">{{ type.name }}</span>
                <div class="bar-container">
                  <div
                    class="bar-fill"
                    :style="{
                      width: getBarWidth(graphStats.by_type?.[type.label] || 0) + '%',
                      background: type.color
                    }"
                  ></div>
                </div>
                <span class="type-count">{{ graphStats.by_type?.[type.label] || 0 }}</span>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 搜索结果面板 -->
        <el-card class="search-results-card" v-if="searchResults.length > 0">
          <template #header>
            <div class="results-header">
              <span>搜索结果</span>
              <el-button text @click="searchResults = []">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="search-results">
            <div
              v-for="result in searchResults"
              :key="result.id"
              class="search-result-item"
              @click="handleSearchResultClick(result)"
            >
              <el-tag size="small" :style="{ background: getNodeColor(result.label), border: 'none', color: '#fff' }">
                {{ getNodeTypeName(result.label) }}
              </el-tag>
              <span class="result-name">{{ result.name }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 路径探索弹窗 -->
    <el-dialog
      v-model="showPathExplorer"
      title="路径探索"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="path-explorer">
        <div class="path-inputs">
          <el-select
            v-model="pathFrom"
            filterable
            remote
            placeholder="起始节点"
            :remote-method="searchNodeForPath"
            style="width: 45%;"
          >
            <el-option
              v-for="node in pathSearchResults"
              :key="node.id"
              :label="node.name"
              :value="node.name"
            />
          </el-select>
          <span class="path-arrow">→</span>
          <el-select
            v-model="pathTo"
            filterable
            remote
            placeholder="目标节点"
            :remote-method="searchNodeForPath"
            style="width: 45%;"
          >
            <el-option
              v-for="node in pathSearchResults"
              :key="node.id"
              :label="node.name"
              :value="node.name"
            />
          </el-select>
        </div>

        <div class="path-options">
          <span>最大深度：</span>
          <el-select v-model="pathMaxDepth" style="width: 100px;">
            <el-option :value="2" label="2" />
            <el-option :value="3" label="3" />
            <el-option :value="4" label="4" />
          </el-select>
        </div>

        <el-button type="primary" @click="findPaths" :loading="findingPath" style="width: 100%;">
          查找路径
        </el-button>

        <div v-if="foundPaths.length > 0" class="paths-results">
          <div class="paths-title">找到 {{ foundPaths.length }} 条路径：</div>
          <div
            v-for="(path, idx) in foundPaths"
            :key="idx"
            class="path-item"
            @click="highlightPath(path)"
          >
            <span class="path-index">{{ idx + 1 }}</span>
            <div class="path-nodes">
              <span
                v-for="(node, nodeIdx) in path.nodes"
                :key="nodeIdx"
                class="path-node"
              >
                <span class="node-label" :style="{ background: getNodeColor(node.label) }">
                  {{ getNodeTypeName(node.label) }}
                </span>
                <span class="node-name">{{ node.name }}</span>
                <span v-if="nodeIdx < path.nodes.length - 1" class="path-rel">
                  {{ getRelationName(path.edges[nodeIdx]?.type) }}
                </span>
              </span>
            </div>
          </div>
        </div>

        <div v-if="pathError" class="path-error">
          {{ pathError }}
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  RefreshRight, FullScreen, Guide, Loading, Connection,
  Close, Plus, Search, Box
} from '@element-plus/icons-vue'
import { graphApi } from '@/api'

// 节点类型配置
const nodeTypes = [
  { label: 'Law', name: '法规', color: '#409eff' },
  { label: 'Article', name: '条款', color: '#1a3a6b' },
  { label: 'Case', name: '案例', color: '#67c23a' },
  { label: 'Penalty', name: '处罚', color: '#f56c6c' },
  { label: 'Standard', name: '标准', color: '#909399' },
  { label: 'Subject', name: '主体', color: '#e6a23c' },
  { label: 'Behavior', name: '行为', color: '#9b59b6' }
]

// 关系类型映射
const relationNames = {
  'CONTAINS': '包含',
  'REFERS': '引用',
  'DEFINES': '规定',
  'TRIGGERS': '触发',
  'APPLIES': '适用',
  'INVOLVES': '涉及',
  'IMPOSES': '施加',
  'EXTRACTED_FROM': '抽取自'
}

// 图数据
const nodes = ref([])
const edges = ref([])
const graphStats = reactive({
  available: false,
  total_nodes: 0,
  total_edges: 0,
  by_type: {}
})

// 状态
const loading = ref(false)
const searchKeyword = ref('')
const typeFilter = ref([])
const searchResults = ref([])
const selectedNode = ref(null)
const nodeRelations = ref([])

// 图谱实例
let network = null
const graphContainer = ref(null)
const networkRef = ref(null)

// 路径探索
const showPathExplorer = ref(false)
const pathFrom = ref('')
const pathTo = ref('')
const pathMaxDepth = ref(3)
const findingPath = ref(false)
const foundPaths = ref([])
const pathError = ref('')
const pathSearchResults = ref([])

// 获取节点颜色
const getNodeColor = (label) => {
  const type = nodeTypes.find(t => t.label === label)
  return type ? type.color : '#909399'
}

// 获取节点类型名称
const getNodeTypeName = (label) => {
  const type = nodeTypes.find(t => t.label === label)
  return type ? type.name : label
}

// 获取关系名称
const getRelationName = (type) => {
  return relationNames[type] || type
}

// 获取条形宽度
const getBarWidth = (count) => {
  if (!graphStats.total_nodes) return 0
  return Math.min(100, (count / graphStats.total_nodes) * 100)
}

// 初始化图谱
const initGraph = async () => {
  loading.value = true
  try {
    // 获取统计信息
    const statsRes = await graphApi.explorerStats()
    if (statsRes.available) {
      graphStats.available = true
      graphStats.total_nodes = statsRes.total_nodes
      graphStats.total_edges = statsRes.total_edges
      graphStats.by_type = statsRes.by_type || {}
    } else {
      graphStats.available = false
    }

    // 获取中心节点
    const centerRes = await graphApi.centerNodes(50)
    if (centerRes.nodes) {
      nodes.value = centerRes.nodes.map(n => ({
        id: n.id,
        label: n.name,
        title: n.name,
        type: n.label,
        degree: n.degree || 0
      }))
    }
    if (centerRes.edges) {
      edges.value = centerRes.edges.map(e => ({
        id: e.id,
        from: e.source,
        to: e.target,
        label: getRelationName(e.type)
      }))
    }

    // 等待 DOM 更新后渲染
    await nextTick()
    renderNetwork()
  } catch (error) {
    console.error('初始化图谱失败:', error)
    ElMessage.error('图谱加载失败')
  } finally {
    loading.value = false
  }
}

// 渲染图谱
const renderNetwork = () => {
  if (!networkRef.value || typeof window === 'undefined') return

  // 动态导入 vis-network
  import('vis-network').then(({ Network, DataSet }) => {
    if (!networkRef.value) return

    // 转换数据格式
    const visNodes = new DataSet(nodes.value.map(n => ({
      id: n.id,
      label: n.label.length > 15 ? n.label.slice(0, 15) + '...' : n.label,
      title: n.title,
      color: {
        background: getNodeColor(n.type),
        border: '#ffffff',
        highlight: { background: getNodeColor(n.type), border: '#409eff' }
      },
      font: { color: '#ffffff', size: 12 },
      type: n.type
    })))

    const visEdges = new DataSet(edges.value.map(e => ({
      id: e.id,
      from: e.from,
      to: e.to,
      label: e.label,
      color: { color: '#7b8db5', highlight: '#409eff' },
      font: { color: '#5a6b85', size: 10, strokeWidth: 0 },
      arrows: 'to'
    })))

    // 创建网络
    network = new Network(
      networkRef.value,
      { nodes: visNodes, edges: visEdges },
      {
        physics: { enabled: true, solver: 'forceAtlas2Based' },
        nodes: { shape: 'dot', size: 20 },
        edges: { smooth: { type: 'continuous' } },
        interaction: { hover: true, tooltipDelay: 200 }
      }
    )

    // 事件处理
    network.on('click', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0]
        const node = nodes.value.find(n => n.id === nodeId)
        if (node) {
          selectNode(node)
        }
      }
    })

    network.on('doubleClick', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0]
        const node = nodes.value.find(n => n.id === nodeId)
        if (node) {
          expandNode(node.label)
        }
      }
    })
  })
}

// 选择节点
const selectNode = async (node) => {
  selectedNode.value = node
  nodeRelations.value = []

  try {
    const res = await graphApi.nodeRelations(node.name)
    if (res.relations) {
      nodeRelations.value = res.relations
    }
  } catch (error) {
    console.error('获取节点关系失败:', error)
  }
}

// 展开邻居
const expandNode = async (nodeName) => {
  loading.value = true
  try {
    const res = await graphApi.neighbors(nodeName, 1)
    if (res.nodes) {
      // 合并新节点
      const existingIds = new Set(nodes.value.map(n => n.id))
      const newNodes = res.nodes.filter(n => !existingIds.has(n.id))
      newNodes.forEach(n => {
        nodes.value.push({
          id: n.id,
          label: n.name,
          title: n.name,
          type: n.label,
          degree: 0
        })
      })

      // 合并新边
      const existingEdgeIds = new Set(edges.value.map(e => e.id))
      const newEdges = res.edges.filter(e => !existingEdgeIds.has(e.id))
      newEdges.forEach(e => {
        edges.value.push({
          id: e.id,
          from: e.source,
          to: e.target,
          label: getRelationName(e.type)
        })
      })

      // 重新渲染
      await nextTick()
      renderNetwork()
      ElMessage.success(`已展开 ${newNodes.length} 个新节点`)
    }
  } catch (error) {
    console.error('展开邻居失败:', error)
    ElMessage.error('展开失败')
  } finally {
    loading.value = false
  }
}

// 重置视图
const resetView = () => {
  if (network) {
    network.fit()
  }
}

// 适应画布
const fitView = () => {
  if (network) {
    network.fit({ animation: true })
  }
}

// 搜索
const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    return
  }

  try {
    const res = await graphApi.searchNodes(searchKeyword.value, null, 20)
    if (res.results) {
      searchResults.value = res.results
      if (res.results.length === 0) {
        ElMessage.info('未找到匹配的实体')
      }
    }
  } catch (error) {
    console.error('搜索失败:', error)
  }
}

// 类型筛选
const handleTypeFilterChange = () => {
  // 实际应用中这里会过滤显示的节点
  // 当前简单实现：仅高亮，不实际过滤
}

// 清空筛选
const clearFilters = () => {
  searchKeyword.value = ''
  typeFilter.value = []
  searchResults.value = []
}

// 处理搜索结果点击
const handleSearchResultClick = (result) => {
  // 在图谱中定位并高亮
  const node = nodes.value.find(n => n.id === result.id)
  if (node) {
    selectNode(node)
    // 居中显示节点
    if (network && network.body) {
      network.focus(node.id, { scale: 1.5, animation: true })
    }
  } else {
    // 如果节点不在当前图谱中，先搜索再添加
    ElMessage.info('正在从服务器加载节点...')
    loadNodeAndFocus(result.id, result.name)
  }
}

// 加载节点并聚焦
const loadNodeAndFocus = async (nodeId, nodeName) => {
  try {
    const res = await graphApi.neighbors(nodeName, 1)
    if (res.nodes) {
      const newNodes = res.nodes.filter(n => !nodes.value.find(existing => existing.id === n.id))
      newNodes.forEach(n => {
        nodes.value.push({
          id: n.id,
          label: n.name,
          title: n.name,
          type: n.label,
          degree: 0
        })
      })

      if (res.edges) {
        const newEdges = res.edges.filter(e => !edges.value.find(existing => existing.id === e.id))
        newEdges.forEach(e => {
          edges.value.push({
            id: e.id,
            from: e.source,
            to: e.target,
            label: getRelationName(e.type)
          })
        })
      }

      await nextTick()
      renderNetwork()

      // 聚焦到目标节点
      const targetNode = nodes.value.find(n => n.name === nodeName)
      if (targetNode) {
        selectNode(targetNode)
        if (network) {
          network.focus(targetNode.id, { scale: 1.5, animation: true })
        }
      }
    }
  } catch (error) {
    ElMessage.error('加载节点失败')
  }
}

// 处理关系点击
const handleRelationClick = (rel) => {
  const targetName = rel.direction === 'outgoing' ? rel.target_name : rel.source_name
  const targetNode = nodes.value.find(n => n.name === targetName)
  if (targetNode) {
    selectNode(targetNode)
    if (network) {
      network.focus(targetNode.id, { scale: 1.5, animation: true })
    }
  } else {
    loadNodeAndFocus(null, targetName)
  }
}

// 切换类型过滤
const toggleTypeFilter = (type) => {
  const idx = typeFilter.value.indexOf(type)
  if (idx > -1) {
    typeFilter.value.splice(idx, 1)
  } else {
    typeFilter.value.push(type)
  }
}

// 路径探索
const searchNodeForPath = async (query) => {
  if (!query) {
    pathSearchResults.value = []
    return
  }

  try {
    const res = await graphApi.searchNodes(query, null, 10)
    if (res.results) {
      pathSearchResults.value = res.results
    }
  } catch (error) {
    console.error('搜索失败:', error)
  }
}

// 查找路径
const findPaths = async () => {
  if (!pathFrom.value || !pathTo.value) {
    ElMessage.warning('请选择起始和目标节点')
    return
  }

  findingPath.value = true
  pathError.value = ''
  foundPaths.value = []

  try {
    // 调用现有的路径查找API
    const res = await fetch(`/api/v1/graph/neo4j/path?from_name=${encodeURIComponent(pathFrom.value)}&to_name=${encodeURIComponent(pathTo.value)}&max_depth=${pathMaxDepth.value}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    const data = await res.json()

    if (data.paths) {
      foundPaths.value = data.paths
    } else if (data.error) {
      pathError.value = data.error
    }
  } catch (error) {
    console.error('查找路径失败:', error)
    pathError.value = '查找路径失败'
  } finally {
    findingPath.value = false
  }
}

// 高亮路径
const highlightPath = (path) => {
  // 在图谱中高亮显示路径
  if (network) {
    const nodeIds = path.nodes.map(n => n.id)
    const edgeIds = path.edges.map(e => e.id)

    // 暂时用点击的方式聚焦第一个节点
    const firstNode = path.nodes[0]
    if (firstNode) {
      const node = nodes.value.find(n => n.name === firstNode.name)
      if (node) {
        selectNode(node)
        if (network) {
          network.focus(node.id, { scale: 1.5, animation: true })
        }
      }
    }
  }
}

onMounted(() => {
  initGraph()
})

onUnmounted(() => {
  if (network) {
    network.destroy()
    network = null
  }
})
</script>

<style scoped>
.graph-explorer-page {
  max-width: 1600px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.graph-card,
.detail-card,
.stats-card,
.search-results-card {
  margin-bottom: 16px;
}

.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.graph-controls {
  display: flex;
  gap: 8px;
}

.graph-container {
  position: relative;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 8px;
  min-height: 500px;
}

.network-canvas {
  width: 100%;
  height: 500px;
}

.graph-legend {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 12px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.legend-item:hover {
  background: #f5f7fa;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-count {
  color: #909399;
  font-size: 12px;
}

.graph-loading,
.graph-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #909399;
}

.graph-empty .hint {
  font-size: 12px;
  color: #c0c4cc;
}

.search-toolbar {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-top: 1px solid #e4e7ed;
  margin-top: 12px;
}

/* 节点详情面板 */
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.node-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.node-type-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  color: #fff;
  font-size: 12px;
  width: fit-content;
}

.node-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  word-break: break-all;
}

.detail-section {
  border-top: 1px solid #e4e7ed;
  padding-top: 12px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}

.relations-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.relation-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s;
}

.relation-item:hover {
  background: #e4e7ed;
}

.rel-type {
  color: #409eff;
  font-weight: 500;
}

.rel-arrow {
  color: #909399;
}

.rel-target {
  color: #303133;
}

.empty-relations {
  color: #c0c4cc;
  font-size: 13px;
  text-align: center;
  padding: 16px;
}

.detail-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

/* 统计面板 */
.stats-content {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #409eff;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.type-distribution {
  border-top: 1px solid #e4e7ed;
  padding-top: 12px;
}

.type-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.type-bar-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-name {
  width: 50px;
  font-size: 12px;
  color: #606266;
}

.bar-container {
  flex: 1;
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.type-count {
  width: 40px;
  font-size: 12px;
  color: #909399;
  text-align: right;
}

/* 搜索结果 */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.search-result-item:hover {
  background: #e4e7ed;
}

.result-name {
  font-size: 13px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 路径探索 */
.path-explorer {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.path-inputs {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.path-arrow {
  font-size: 20px;
  color: #409eff;
}

.path-options {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 14px;
}

.paths-results {
  border-top: 1px solid #e4e7ed;
  padding-top: 16px;
  max-height: 300px;
  overflow-y: auto;
}

.paths-title {
  font-size: 13px;
  color: #606266;
  margin-bottom: 12px;
}

.path-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.path-item:hover {
  background: #e4e7ed;
}

.path-index {
  width: 20px;
  height: 20px;
  background: #409eff;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}

.path-nodes {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.path-node {
  display: flex;
  align-items: center;
  gap: 4px;
}

.node-label {
  padding: 2px 6px;
  border-radius: 2px;
  font-size: 10px;
  color: #fff;
}

.node-name {
  font-size: 12px;
  color: #303133;
}

.path-rel {
  color: #909399;
  font-size: 12px;
  margin: 0 4px;
}

.path-error {
  color: #f56c6c;
  font-size: 13px;
  text-align: center;
  padding: 12px;
}
</style>