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
                <el-button size="small" @click="handleQuickAction('cases')" title="处罚案例">
                  <el-icon><Document /></el-icon>
                </el-button>
                <el-button size="small" @click="handleQuickAction('laws')" title="相关法规">
                  <el-icon><Folder /></el-icon>
                </el-button>
                <el-button size="small" @click="handleQuickAction('random')" title="随便看看">
                  <el-icon><Refresh /></el-icon>
                </el-button>
                <el-divider direction="vertical" />
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
              <div
                v-for="type in nodeTypes"
                :key="type.label"
                class="legend-item-wrapper"
              >
                <el-popover
                  placement="right"
                  :width="280"
                  trigger="hover"
                  @show="loadTypeExamples(type.label)"
                >
                  <template #reference>
                    <div class="legend-item" @click.stop="handleLegendClick(type.label)">
                      <span class="legend-dot" :style="{ background: type.color }"></span>
                      <span>{{ type.name }}</span>
                      <span class="legend-count">({{ graphStats.by_type?.[type.label] || 0 }})</span>
                    </div>
                  </template>
                  <div class="legend-popover">
                    <div class="popover-title">{{ type.name }}</div>
                    <div class="popover-desc">{{ type.description }}</div>
                    <el-divider style="margin: 8px 0" />
                    <div class="popover-section">示例节点</div>
                    <div v-if="typeExamples[type.label]?.length" class="popover-examples">
                      <el-tag
                        v-for="ex in typeExamples[type.label]"
                        :key="ex.id"
                        size="small"
                        class="example-tag"
                        @click="handleExampleClick(ex)"
                      >
                        {{ ex.name }}
                      </el-tag>
                    </div>
                    <div v-else class="popover-empty">暂无示例</div>
                  </div>
                </el-popover>
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

            <!-- 引导探索面板 -->
            <div v-if="showGuidePanel && !loading" class="guide-panel">
              <div class="guide-title">
                <el-icon><Guide /></el-icon>
                <span>探索知识图谱</span>
              </div>
              <p class="guide-subtitle">输入关键词，或选择下面的示例问题开始探索</p>
              <div class="guide-questions">
                <el-button
                  v-for="q in guideQuestions"
                  :key="q.text"
                  @click="handleGuideQuestion(q)"
                  type="primary" plain
                  class="guide-btn"
                >
                  {{ q.text }}
                </el-button>
              </div>
              <div class="guide-tips">
                <el-tag size="small" type="info">提示</el-tag>
                <span>您可以搜索实体名称，或直接点击图例筛选特定类型的节点</span>
              </div>
              <el-button text @click="showGuidePanel = false" class="skip-btn">
                跳过引导 →
              </el-button>
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

          <!-- 搜索结果面板 -->
          <div class="search-results-inline" v-if="searchResults.length > 0">
            <div class="results-header">
              <span>搜索结果 ({{ searchResults.length }})</span>
              <el-button text @click="searchResults = []" size="small">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
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
            <div class="node-type-tag" :style="{ background: getNodeColor(selectedNode.type || selectedNode.label) }">
              {{ getNodeTypeName(selectedNode.type || selectedNode.label) }}
            </div>
            <div class="node-name">{{ selectedNode.name }}</div>

            <!-- 操作按钮 -->
            <div class="detail-actions">
              <el-button type="primary" size="small" @click="viewNodeDetail">
                <el-icon><Document /></el-icon>
                查看详情
              </el-button>
              <el-button size="small" @click="expandNode(selectedNode.name)">
                <el-icon><Plus /></el-icon>
                展开邻居
              </el-button>
              <el-button size="small" @click="findSimilarNodes">
                <el-icon><Search /></el-icon>
                发现相似
              </el-button>
            </div>

            <!-- 关联关系 -->
            <div class="detail-section">
              <div class="section-title">关联关系 ({{ nodeRelations.length }})</div>
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

            <!-- 相关推荐 -->
            <div class="detail-section">
              <div class="section-title">相关推荐</div>
              <div v-if="relatedRecommendations.length > 0" class="recommendations-list">
                <div
                  v-for="rec in relatedRecommendations"
                  :key="rec.id"
                  class="recommendation-item"
                  @click="loadNodeAndFocus(rec.id, rec.name)"
                >
                  <el-tag size="small" :style="{ background: getNodeColor(rec.label), border: 'none', color: '#fff' }">
                    {{ getNodeTypeName(rec.label) }}
                  </el-tag>
                  <span class="rec-name">{{ rec.name }}</span>
                </div>
              </div>
              <div v-else class="empty-recommendations">
                <el-button text size="small" @click="loadRelatedRecommendations">
                  点击加载相关推荐
                </el-button>
              </div>
            </div>

            <!-- 智能提示 -->
            <div v-if="selectedNode && nodeRelations.length > 0" class="node-hint">
              <div class="hint-title">
                <el-icon><InfoFilled /></el-icon>
                关联洞察
              </div>
              <div class="hint-content">
                <div class="hint-stat">
                  该<span style="font-weight: 600;">{{ getNodeTypeName(selectedNode.type || selectedNode.label) }}</span>关联了
                  <span class="stat-num">{{ nodeRelations.length }}</span>个实体
                </div>
                <div class="hint-stat">
                  涉及
                  <span class="stat-num">{{ relatedTypesCount }}</span>
                  种不同类型
                </div>
              </div>
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
import { ref, reactive, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  RefreshRight, FullScreen, Guide, Loading, Connection,
  Close, Plus, Search, Box, Document, Folder, Refresh, InfoFilled
} from '@element-plus/icons-vue'
import { graphApi } from '@/api'

const router = useRouter()

// 节点类型配置
const nodeTypes = [
  { label: 'Law', name: '法规', color: '#409eff', description: '国家或地方发布的政策文件、条例、规定等' },
  { label: 'Article', name: '条款', color: '#1a3a6b', description: '法规中的具体条文内容，包括章节条款' },
  { label: 'Case', name: '案例', color: '#67c23a', description: '实际发生的行政处罚案例，记录违法事实和处罚结果' },
  { label: 'Penalty', name: '处罚', color: '#f56c6c', description: '针对违法行为的处罚决定，包括罚款、吊销等' },
  { label: 'Standard', name: '标准', color: '#909399', description: '行业技术标准、规范，是合规参考的重要依据' },
  { label: 'Subject', name: '主体', color: '#e6a23c', description: '涉及的个人或单位，如企业、法人、责任人' },
  { label: 'Behavior', name: '行为', color: '#9b59b6', description: '违法行为或具体行为描述' }
]

// 类型示例数据
const typeExamples = ref({
  Law: [],
  Article: [],
  Case: [],
  Penalty: [],
  Standard: [],
  Subject: [],
  Behavior: []
})

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

// 引导问题配置
const guideQuestions = [
  { text: '查找海南省住建领域的处罚案例', search: '海南', type: 'Case' },
  { text: '了解某法规的引用关系', search: '法规', type: 'Law' },
  { text: '某主体的关联行为有哪些', search: '', type: 'Subject' },
  { text: '查找建筑节能相关标准', search: '建筑节能', type: 'Standard' },
  { text: '了解处罚决定的触发条件', search: '', type: 'Penalty' }
]

// 处理引导问题点击
const handleGuideQuestion = (q) => {
  searchKeyword.value = q.search
  if (q.type) {
    typeFilter.value = [q.type]
  }
  showGuidePanel.value = false
  handleSearch()
}

// 加载类型示例
const loadTypeExamples = async (label) => {
  if (typeExamples.value[label]?.length > 0) return
  try {
    const res = await graphApi.searchNodes('', label, 3)
    if (res.results) {
      typeExamples.value[label] = res.results
    }
  } catch (error) {
    console.error('加载示例失败:', error)
  }
}

// 点击示例节点
const handleExampleClick = (example) => {
  searchKeyword.value = example.name
  showGuidePanel.value = false
  handleSearch()
}

// 快捷操作处理
const handleQuickAction = async (action) => {
  console.log('handleQuickAction 被调用, action:', action)
  showGuidePanel.value = false
  loading.value = true
  try {
    let results = []
    switch (action) {
      case 'cases':
        // 获取处罚案例
        const casesRes = await graphApi.searchNodes('', 'Case', 20)
        results = casesRes.results || []
        break
      case 'laws':
        // 获取法规
        console.log('开始获取法规...')
        try {
          const lawsRes = await graphApi.searchNodes('', 'Law', 20)
          console.log('法规搜索结果:', lawsRes)
          results = lawsRes.results || []
        } catch (e) {
          console.error('法规搜索失败:', e)
          results = []
        }
        break
      case 'random':
        // 随机获取中心节点
        const centerRes = await graphApi.centerNodes(30)
        results = (centerRes.nodes || []).map(n => ({ id: n.id, name: n.name, label: n.label }))
        break
    }
    if (results.length > 0) {
      console.log('准备加载到图谱的节点:', results)
      await loadResultsToGraph(results)
      ElMessage.success(`已加载 ${results.length} 个实体`)
    } else {
      ElMessage.warning('暂无数据')
    }
  } catch (error) {
    console.error('快捷操作失败:', error)
    ElMessage.error('加载失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 计算关联类型数
const relatedTypesCount = computed(() => {
  if (!selectedNode.value || !nodeRelations.value.length) return 0
  const types = new Set()
  nodeRelations.value.forEach(rel => {
    if (rel.target_label) types.add(rel.target_label)
    if (rel.source_label) types.add(rel.source_label)
  })
  return types.size
})

// 图数据
const nodes = ref([])
const edges = ref([])
const showGuidePanel = ref(true)
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
const relatedRecommendations = ref([])

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

// 监听类型筛选变化
watch(typeFilter, (newFilter) => {
  if (network && nodes.value.length > 0) {
    const filteredIds = new Set(newFilter.length > 0
      ? nodes.value.filter(n => newFilter.includes(n.label)).map(n => n.id)
      : nodes.value.map(n => n.id))

    // 通过设置 opacity 来过滤
    const allNodes = network.body.data.nodes.get()
    allNodes.forEach(node => {
      network.body.data.nodes.update({
        id: node.id,
        hidden: filteredIds.size > 0 && !filteredIds.has(node.id)
      })
    })

    // 同步过滤边
    const allEdges = network.body.data.edges.get()
    allEdges.forEach(edge => {
      const sourceHidden = network.body.data.nodes.get(edge.from)?.hidden
      const targetHidden = network.body.data.nodes.get(edge.to)?.hidden
      network.body.data.edges.update({
        id: edge.id,
        hidden: filteredIds.size > 0 && (sourceHidden || targetHidden)
      })
    })
  }
})

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
      nodes.value = centerRes.nodes
        .filter(n => n.name) // 过滤无名称的节点
        .map(n => ({
          id: n.id,
          name: n.name,
          label: n.label || n.name,
          title: n.name,
          type: n.label || '',
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
  console.log('renderNetwork 被调用, 节点数:', nodes.value.length)
  if (!networkRef.value || typeof window === 'undefined') return

  // 动态导入 vis-network
  import('vis-network').then(({ Network }) => {
  import('vis-data').then(({ DataSet }) => {
    if (!networkRef.value) return

    // 去重节点（同一节点可能出现在多条边中）
    const uniqueNodes = Array.from(
      new Map(nodes.value.map(n => [n.id, n])).values()
    )

    // 转换数据格式
    const visNodes = new DataSet(uniqueNodes.map(n => ({
      id: n.id,
      label: (n.name || n.label || '').length > 15 ? (n.name || n.label || '').slice(0, 15) + '...' : (n.name || n.label || ''),
      title: n.title || n.name || n.label,
      color: {
        background: getNodeColor(n.type),
        border: '#ffffff',
        highlight: { background: getNodeColor(n.type), border: '#409eff' }
      },
      font: { color: '#ffffff', size: 12, strokeWidth: 2, strokeColor: '#000000' },
      type: n.type
    })))

    // 去重边
    const uniqueEdges = Array.from(
      new Map(edges.value.map(e => [e.id, e])).values()
    )

    const visEdges = new DataSet(uniqueEdges.map(e => ({
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
      } else if (params.edges.length > 0) {
        // 点击边，高亮显示引用路径
        const edgeId = params.edges[0]
        highlightEdgePath(edgeId)
      }
    })

    network.on('doubleClick', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0]
        const node = nodes.value.find(n => n.id === nodeId)
        if (node) {
          expandNode(node.name || node.label)
        }
      }
    })

    // 鼠标悬停在边上时显示关系信息
    network.on('hoverEdge', (params) => {
      const edge = edges.value.find(e => e.id === params.edge)
      if (edge) {
        network.body.container.style.cursor = 'pointer'
      }
    })

    network.on('blurEdge', (params) => {
      network.body.container.style.cursor = 'default'
    })
  })
  })
}

// 高亮边及其关联的节点
const highlightEdgePath = (edgeId) => {
  if (!network) return

  const edge = edges.value.find(e => e.id === edgeId)
  if (!edge) return

  // 获取边关联的两个节点ID
  const connectedNodeIds = [edge.from, edge.to]

  // 重置所有节点和边的样式
  const allNodes = network.body.data.nodes.get()
  const allEdges = network.body.data.edges.get()

  allNodes.forEach(node => {
    network.body.data.nodes.update({
      id: node.id,
      color: {
        background: getNodeColor(node.type),
        border: '#ffffff',
        highlight: { background: getNodeColor(node.type), border: '#409eff' }
      },
      borderWidth: 1
    })
  })

  allEdges.forEach(e => {
    network.body.data.edges.update({
      id: e.id,
      color: { color: '#7b8db5', highlight: '#409eff' },
      width: 1
    })
  })

  // 高亮当前边和关联节点
  network.body.data.edges.update({
    id: edgeId,
    color: { color: '#409eff', highlight: '#67c23a' },
    width: 3
  })

  connectedNodeIds.forEach(nodeId => {
    network.body.data.nodes.update({
      id: nodeId,
      borderWidth: 3,
      color: {
        background: getNodeColor(network.body.data.nodes.get(nodeId)?.type),
        border: '#409eff',
        highlight: { background: getNodeColor(network.body.data.nodes.get(nodeId)?.type), border: '#67c23a' }
      }
    })
  })

  // 2秒后恢复
  setTimeout(() => {
    allEdges.forEach(e => {
      network.body.data.edges.update({
        id: e.id,
        color: { color: '#7b8db5', highlight: '#409eff' },
        width: 1
      })
    })
    connectedNodeIds.forEach(nodeId => {
      network.body.data.nodes.update({
        id: nodeId,
        borderWidth: 1
      })
    })
  }, 2000)
}

// 选择节点
const selectNode = async (node) => {
  if (!node) return
  selectedNode.value = node
  nodeRelations.value = []

  const nodeName = node.name || node.label || node.title
  if (!nodeName) {
    console.warn('选择节点失败: 节点名称为空', node)
    return
  }

  try {
    const res = await graphApi.nodeRelations(nodeName)
    if (res.relations) {
      nodeRelations.value = res.relations
    }
  } catch (error) {
    console.error('获取节点关系失败:', error)
  }
}

// 查看节点详情（跳转到知识详情页）
const viewNodeDetail = () => {
  if (!selectedNode.value || !selectedNode.value.id) {
    ElMessage.warning('节点信息不完整')
    return
  }
  router.push(`/knowledge/detail/${selectedNode.value.id}`)
}

// 查找相似节点
const findSimilarNodes = async () => {
  if (!selectedNode.value) return
  loading.value = true
  try {
    const res = await graphApi.searchNodes(selectedNode.value.name, null, 10)
    if (res.results?.length > 0) {
      const similar = res.results.filter(r => r.id !== selectedNode.value.id).slice(0, 5)
      if (similar.length > 0) {
        await loadResultsToGraph(similar)
        ElMessage.success(`已加载 ${similar.length} 个相似实体`)
      } else {
        ElMessage.info('没有找到相似实体')
      }
    } else {
      ElMessage.info('没有找到相似实体')
    }
  } catch (error) {
    console.error('查找相似节点失败:', error)
    ElMessage.error('查找失败')
  } finally {
    loading.value = false
  }
}

// 加载相关推荐
const loadRelatedRecommendations = async () => {
  if (!selectedNode.value) return
  try {
    const res = await graphApi.neighbors(selectedNode.value.name, 2)
    if (res.nodes) {
      // 获取二级邻居作为推荐
      const recommendations = res.nodes
        .filter(n => n.id !== selectedNode.value.id)
        .slice(0, 5)
        .map(n => ({ id: n.id, name: n.name, label: n.label }))
      relatedRecommendations.value = recommendations
      if (recommendations.length === 0) {
        ElMessage.info('暂无相关推荐')
      }
    }
  } catch (error) {
    console.error('加载相关推荐失败:', error)
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
        if (!n.name) return // 跳过无名称的节点
        nodes.value.push({
          id: n.id,
          name: n.name,
          label: n.label || n.name,
          title: n.title || n.name,
          type: n.label || '',
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
      } else if (res.results.length > 0 && res.results.length <= 5) {
        // 少量结果，直接加载到图谱
        await loadResultsToGraph(res.results)
        ElMessage.success(`已加载 ${res.results.length} 个相关实体到图谱`)
      }
    }
  } catch (error) {
    console.error('搜索失败:', error)
  }
}

// 加载搜索结果到图谱
const loadResultsToGraph = async (results) => {
  console.log('loadResultsToGraph 被调用, 结果数量:', results.length)
  // 先清空当前图谱
  nodes.value = []
  edges.value = []

  const newNodes = []
  const newEdges = []
  const nodeIds = new Set()

  for (const result of results) {
    console.log('处理节点:', result)
    if (!nodeIds.has(result.id) && result.name) {
      newNodes.push({
        id: result.id,
        name: result.name,
        label: result.label || result.name,
        title: result.name,
        type: result.label || '',
        degree: 0
      })
      nodeIds.add(result.id)
    }

    // 获取邻居节点
    try {
      const neighbors = await graphApi.neighbors(result.name, 1)
      console.log(`节点 ${result.name} 的邻居:`, neighbors)
      if (neighbors.nodes) {
        for (const n of neighbors.nodes) {
          if (!nodeIds.has(n.id) && n.name) {
            newNodes.push({
              id: n.id,
              name: n.name,
              label: n.label || n.name,
              title: n.name,
              type: n.label || '',
              degree: 0
            })
            nodeIds.add(n.id)
          }
        }
      }
      if (neighbors.edges) {
        for (const e of neighbors.edges) {
          newEdges.push({
            id: e.id,
            from: e.source,
            to: e.target,
            label: getRelationName(e.type)
          })
        }
      }
    } catch (e) {
      console.error('获取邻居失败:', e)
    }
  }

  nodes.value = newNodes
  edges.value = newEdges
  console.log('设置后的节点:', nodes.value.length, '边:', edges.value.length)

  // 等待 DOM 更新后渲染
  await nextTick()
  if (network) {
    network.destroy()
    network = null
  }
  renderNetwork()
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
        if (!n.name) return // 跳过无名称的节点
        nodes.value.push({
          id: n.id,
          name: n.name,
          label: n.label || n.name,
          title: n.title || n.name,
          type: n.label || '',
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

// 图例点击处理
const handleLegendClick = async (typeLabel) => {
  console.log('handleLegendClick 被调用, typeLabel:', typeLabel)
  ElMessage.info(`正在加载${typeLabel}类型节点...`)
  await toggleTypeFilter(typeLabel)
}

// 切换类型过滤
const toggleTypeFilter = async (type) => {
  console.log('toggleTypeFilter 被调用, type:', type)
  // 点击图例时，直接加载该类型的前20个节点
  console.log('准备调用 searchNodes API')
  try {
    const res = await graphApi.searchNodes('', type, 20)
    console.log('searchNodes 返回:', res)
    if (res.results?.length > 0) {
      console.log('准备调用 loadResultsToGraph')
      await loadResultsToGraph(res.results)
      // 保持该类型选中
      typeFilter.value = [type]
      return
    } else {
      console.log('没有搜索结果')
      ElMessage.warning('暂无数据')
      return
    }
  } catch (e) {
    console.error('加载类型节点失败:', e)
    ElMessage.error('加载失败')
    return
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

/* 引导探索面板 */
.guide-panel {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #fff;
  border-radius: 16px;
  padding: 32px 40px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 100;
  max-width: 500px;
}

.guide-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.guide-subtitle {
  color: #909399;
  margin: 0 0 20px 0;
}

.guide-questions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.guide-btn {
  width: 100%;
  justify-content: flex-start;
  padding-left: 16px;
}

.guide-tips {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #606266;
}

.skip-btn {
  color: #909399;
  font-size: 13px;
}

.skip-btn:hover {
  color: #409eff;
}

/* 图例 popover */
.legend-popover {
  padding: 4px 0;
}

.popover-title {
  font-weight: 600;
  font-size: 15px;
  color: #303133;
  margin-bottom: 4px;
}

.popover-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.popover-section {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.popover-examples {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.example-tag {
  cursor: pointer;
}

.example-tag:hover {
  opacity: 0.8;
}

.popover-empty {
  font-size: 12px;
  color: #c0c4cc;
}

/* 节点详情智能提示 */
.node-hint {
  background: #ecf5ff;
  border-radius: 8px;
  padding: 12px;
  margin-top: 12px;
}

.hint-title {
  font-size: 12px;
  color: #409eff;
  font-weight: 600;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.hint-content {
  font-size: 13px;
  color: #606266;
}

.hint-stat {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
}

.hint-stat .stat-num {
  font-weight: 600;
  color: #409eff;
}

/* 快捷入口 */
.quick-actions {
  position: absolute;
  bottom: 12px;
  right: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 10;
}

.quick-action-btn {
  width: 120px;
  justify-content: flex-start;
  padding-left: 12px;
}

.search-toolbar {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-top: 1px solid #e4e7ed;
  margin-top: 12px;
}

.search-results-inline {
  border-top: 1px solid #e4e7ed;
  margin-top: 12px;
  padding-top: 12px;
}

.search-results-inline .results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-weight: 500;
}

.search-results-inline .search-results {
  max-height: 200px;
  overflow-y: auto;
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

.empty-recommendations {
  text-align: center;
  padding: 8px;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recommendation-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  background: #f5f7fa;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.recommendation-item:hover {
  background: #e4e7ed;
}

.rec-name {
  font-size: 13px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-actions {
  display: flex;
  flex-wrap: wrap;
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