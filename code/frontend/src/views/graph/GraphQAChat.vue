<template>
  <div class="graph-qa-page">
    <div class="page-header">
      <h2>图谱增强问答 <el-tag type="warning" size="small">Graph-RAG</el-tag></h2>
      <p class="subtitle">基于知识图谱的多跳推理问答，可视化展示推理路径</p>
    </div>

    <el-row :gutter="24">
      <!-- 左侧：对话区域 -->
      <el-col :span="14">
        <el-card class="chat-card">
          <template #header>
            <div class="chat-header">
              <span>问答过程</span>
              <div class="header-actions">
                <el-switch
                  v-model="useNeo4j"
                  active-text="使用Neo4j"
                  inactive-text=""
                />
                <el-switch
                  v-model="showReasoning"
                  active-text="显示推理过程"
                  inactive-text=""
                />
                <el-button text @click="clearHistory">
                  <el-icon><Delete /></el-icon> 清空
                </el-button>
              </div>
            </div>
          </template>

          <div class="chat-messages" ref="chatMessagesRef">
            <!-- 空状态 -->
            <div v-if="!messages.length && !isThinking" class="empty-state">
              <div class="empty-graph">
                <svg width="120" height="120" viewBox="0 0 120 120">
                  <!-- 中心节点 -->
                  <circle cx="60" cy="60" r="16" fill="#1a3a6b" />
                  <text x="60" y="64" text-anchor="middle" fill="#fff" font-size="10">问题</text>
                  <!-- 周围节点 -->
                  <circle cx="30" cy="35" r="10" fill="#409eff" />
                  <circle cx="90" cy="35" r="10" fill="#67c23a" />
                  <circle cx="30" cy="85" r="10" fill="#e6a23c" />
                  <circle cx="90" cy="85" r="10" fill="#f56c6c" />
                  <!-- 连接线 -->
                  <line x1="44" y1="48" x2="26" y2="40" stroke="#dcdfe6" stroke-width="2" />
                  <line x1="76" y1="48" x2="84" y2="40" stroke="#dcdfe6" stroke-width="2" />
                  <line x1="44" y1="72" x2="26" y2="80" stroke="#dcdfe6" stroke-width="2" />
                  <line x1="76" y1="72" x2="84" y2="80" stroke="#dcdfe6" stroke-width="2" />
                </svg>
              </div>
              <p>输入您的问题，体验图谱增强的推理问答</p>
              <div class="example-questions">
                <el-tag
                  v-for="q in exampleQuestions"
                  :key="q"
                  class="example-tag"
                  @click="askExample(q)"
                >
                  {{ q }}
                </el-tag>
              </div>
            </div>

            <!-- 消息列表 -->
            <div v-for="(msg, index) in messages" :key="index" class="chat-message">
              <!-- 用户消息 -->
              <div v-if="msg.role === 'user'" class="message user">
                <div class="message-avatar">
                  <el-avatar :size="36" style="background: #1a3a6b;">我</el-avatar>
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="sender-name">我</span>
                    <span class="message-time">{{ msg.time }}</span>
                  </div>
                  <div class="message-body">
                    {{ msg.content }}
                  </div>
                </div>
              </div>

              <!-- 助手消息 -->
              <div v-else class="message assistant">
                <div class="message-avatar">
                  <el-avatar :size="36" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <el-icon><Connection /></el-icon>
                  </el-avatar>
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="sender-name">图谱助手</span>
                    <span class="message-time">{{ msg.time }}</span>
                  </div>

                  <!-- 推理过程 -->
                  <div v-if="showReasoning && msg.reasoningChain" class="reasoning-section">
                    <div class="reasoning-title">
                      <el-icon><Cpu /></el-icon>
                      <span>推理路径</span>
                    </div>
                    <div class="reasoning-steps">
                      <div
                        v-for="(step, stepIdx) in msg.reasoningChain"
                        :key="stepIdx"
                        class="reasoning-step"
                        :class="{ 'is-expanded': expandedSteps.includes(stepIdx) }"
                        @click="toggleStep(stepIdx)"
                      >
                        <div class="step-number">{{ stepIdx + 1 }}</div>
                        <div class="step-content">
                          <div class="step-query">{{ step.query }}</div>
                          <div class="step-result">{{ step.result }}</div>
                          <div v-if="step.entities?.length" class="step-entities">
                            <el-tag
                              v-for="entity in step.entities"
                              :key="entity"
                              size="small"
                              :type="getEntityType(stepIdx)"
                            >
                              {{ entity }}
                            </el-tag>
                          </div>
                          <!-- 展开详情 -->
                          <div v-if="expandedSteps.includes(stepIdx) && step.details" class="step-details">
                            <div v-if="step.details.search_query" class="detail-item">
                              <span class="detail-label">搜索词：</span>
                              <span class="detail-value">{{ step.details.search_query }}</span>
                            </div>
                            <div v-if="step.details.knowledge_found?.length" class="detail-item">
                              <span class="detail-label">找到的知识：</span>
                              <div class="knowledge-list">
                                <div
                                  v-for="(title, idx) in step.details.knowledge_found"
                                  :key="idx"
                                  class="knowledge-item"
                                >
                                  {{ idx + 1 }}. {{ title }}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div class="step-expand-icon">
                          <el-icon v-if="step.details"><ArrowRight :class="{ 'is-expanded': expandedSteps.includes(stepIdx) }" /></el-icon>
                        </div>
                        <div v-if="stepIdx < msg.reasoningChain.length - 1" class="step-arrow">
                          <el-icon><ArrowRight /></el-icon>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 最终答案 -->
                  <div class="message-body answer">
                    <div v-html="renderMarkdown(msg.content)"></div>
                  </div>

                  <!-- 引用来源 -->
                  <div v-if="msg.citations?.length" class="citations">
                    <div class="citations-title">
                      <el-icon><Document /></el-icon>
                      <span>参考来源</span>
                    </div>
                    <div
                      v-for="citation in msg.citations"
                      :key="citation.id"
                      class="citation-item"
                      @click="highlightNode(citation.id)"
                    >
                      <el-tag size="small" :type="citation.type === 'law' ? 'danger' : 'primary'">
                        {{ citation.typeName }}
                      </el-tag>
                      <span class="citation-title">{{ citation.title }}</span>
                      <el-icon class="citation-link"><View /></el-icon>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 思考中 -->
            <div v-if="isThinking" class="chat-message">
              <div class="message assistant">
                <div class="message-avatar">
                  <el-avatar :size="36" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <el-icon><Connection /></el-icon>
                  </el-avatar>
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="sender-name">图谱助手</span>
                    <span class="thinking-mode" v-if="useNeo4j">
                      <el-tag size="small" type="warning">Neo4j 推理</el-tag>
                    </span>
                  </div>

                  <!-- 推理过程 (实时展示) -->
                  <div class="reasoning-section thinking-reasoning" v-if="liveReasoningChain.length > 0">
                    <div class="reasoning-title">
                      <el-icon><Cpu /></el-icon>
                      <span>推理进行中</span>
                      <span class="reasoning-progress-text">{{ thinkingProgress }}%</span>
                    </div>
                    <div class="reasoning-steps">
                      <div
                        v-for="(step, stepIdx) in liveReasoningChain"
                        :key="stepIdx"
                        class="reasoning-step"
                        :class="{
                          'is-active': stepIdx === liveReasoningChain.length - 1,
                          'is-done': stepIdx < liveReasoningChain.length - 1
                        }"
                      >
                        <div class="step-indicator">
                          <div v-if="stepIdx < liveReasoningChain.length - 1" class="step-check">
                            <el-icon><Check /></el-icon>
                          </div>
                          <div v-else class="step-loading">
                            <el-icon class="is-loading"><Loading /></el-icon>
                          </div>
                        </div>
                        <div class="step-content">
                          <div class="step-query">{{ step.query }}</div>
                          <div class="step-result" :class="{ 'is-calculating': stepIdx === liveReasoningChain.length - 1 }">
                            <template v-if="stepIdx === liveReasoningChain.length - 1">
                              <span class="calc-dots">正在分析</span>
                            </template>
                            <template v-else>
                              {{ step.result }}
                            </template>
                          </div>
                          <div v-if="step.entities?.length" class="step-entities">
                            <el-tag
                              v-for="entity in step.entities"
                              :key="entity"
                              size="small"
                              type="info"
                            >
                              {{ entity }}
                            </el-tag>
                          </div>
                        </div>
                        <div v-if="stepIdx < liveReasoningChain.length - 1" class="step-connector"></div>
                      </div>
                    </div>
                  </div>

                  <!-- 进度条 -->
                  <div class="message-body thinking" v-else>
                    <div class="thinking-progress">
                      <div class="progress-bar">
                        <div class="progress-fill" :style="{ width: thinkingProgress + '%' }"></div>
                      </div>
                      <span class="progress-text">{{ thinkingProgress }}%</span>
                    </div>

                    <!-- 步骤列表 -->
                    <div class="thinking-steps">
                      <div
                        v-for="(step, idx) in thinkingSteps"
                        :key="idx"
                        class="thinking-step"
                        :class="{
                          active: thinkingCurrent === idx,
                          completed: thinkingCurrent > idx
                        }"
                      >
                        <div class="thinking-icon">
                          <el-icon v-if="thinkingCurrent > idx" class="check-icon"><Select /></el-icon>
                          <el-icon v-else-if="thinkingCurrent === idx" class="loading-icon"><Loading /></el-icon>
                          <el-icon v-else class="waiting-icon"><More /></el-icon>
                        </div>
                        <div class="step-info">
                          <span class="step-name">{{ step.name }}</span>
                          <span class="step-detail" v-if="thinkingCurrent === idx && step.detail">{{ step.detail }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- 趣味提示 -->
                    <div class="fun-tip" v-if="thinkingCurrent < thinkingSteps.length">
                      <el-icon><Sunrise /></el-icon>
                      <span>{{ funTips[currentTipIndex] }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="chat-input">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="2"
              placeholder="请输入问题，例如：工地脚手架坠落事故后，处罚依据和标准是什么？"
              @keydown.enter.ctrl="handleSend"
            />
            <div class="input-actions">
              <span class="hint">按 Ctrl+Enter 发送</span>
              <el-button type="primary" @click="handleSend" :disabled="!inputMessage.trim() || isThinking">
                <el-icon><Promotion /></el-icon>
                发送
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：图谱可视化 -->
      <el-col :span="10">
        <el-card class="graph-card">
          <template #header>
            <div class="graph-header">
              <span>知识图谱</span>
              <div class="graph-controls">
                <el-button size="small" @click="resetGraph">
                  <el-icon><Refresh /></el-icon>
                </el-button>
                <el-button size="small" @click="toggleFullscreen">
                  <el-icon><FullScreen /></el-icon>
                </el-button>
              </div>
            </div>
          </template>

          <div class="graph-container" ref="graphContainer">
            <svg ref="graphSvg" width="100%" height="400">
              <!-- 动态渲染图谱 -->
              <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#909399" />
                </marker>
                <marker id="arrowhead-active" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#409eff" />
                </marker>
              </defs>

              <!-- 边 -->
              <g class="edges">
                <transition-group name="edge-fade">
                  <g v-for="edge in graphData.edges" :key="edge.id">
                    <path
                      :d="getEdgePath(edge)"
                      :stroke="highlightedEdges.includes(edge.id) ? '#409eff' : '#dcdfe6'"
                      :stroke-width="highlightedEdges.includes(edge.id) ? 3 : 2"
                      fill="none"
                      :marker-end="highlightedEdges.includes(edge.id) ? 'url(#arrowhead-active)' : 'url(#arrowhead)'"
                      class="edge-path"
                      @mouseenter="highlightEdge(edge)"
                      @mouseleave="unhighlightEdge"
                    />
                    <text
                      :x="(graphData.nodes.find(n => n.id === edge.source)?.x + graphData.nodes.find(n => n.id === edge.target)?.x) / 2"
                      :y="(graphData.nodes.find(n => n.id === edge.source)?.y + graphData.nodes.find(n => n.id === edge.target)?.y) / 2 - 8"
                      text-anchor="middle"
                      class="edge-label"
                      :fill="highlightedEdges.includes(edge.id) ? '#409eff' : '#909399'"
                    >
                      {{ edge.label }}
                    </text>
                  </g>
                </transition-group>
              </g>

              <!-- 节点 -->
              <g class="nodes">
                <transition-group name="node-fade">
                  <g
                    v-for="node in graphData.nodes"
                    :key="node.id"
                    :transform="`translate(${node.x}, ${node.y})`"
                    class="node-group"
                    @click="selectNode(node)"
                    @mouseenter="hoverNode(node.id)"
                    @mouseleave="unhoverNode"
                  >
                    <!-- 节点背景 -->
                    <circle
                      :r="selectedNode?.id === node.id ? 40 : (hoveredNodeId === node.id ? 38 : 35)"
                      :fill="getNodeColor(node.type)"
                      :stroke="selectedNode?.id === node.id || highlightedNodes.includes(node.id) ? '#409eff' : 'transparent'"
                      :stroke-width="3"
                      class="node-circle"
                    />
                    <!-- 节点图标 -->
                    <text
                      y="-5"
                      text-anchor="middle"
                      fill="#fff"
                      font-size="16"
                    >
                      {{ getNodeIcon(node.type) }}
                    </text>
                    <!-- 节点标签 -->
                    <text
                      y="50"
                      text-anchor="middle"
                      :fill="selectedNode?.id === node.id || hoveredNodeId === node.id ? '#303133' : '#606266'"
                      font-size="12"
                      font-weight="500"
                    >
                      {{ node.label.length > 8 ? node.label.slice(0, 8) + '...' : node.label }}
                    </text>
                  </g>
                </transition-group>
              </g>
            </svg>

            <!-- 节点详情面板 -->
            <div v-if="selectedNode" class="node-detail">
              <div class="detail-header">
                <span class="detail-type">{{ getNodeTypeName(selectedNode.type) }}</span>
                <el-button size="small" text @click="selectedNode = null">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
              <div class="detail-title">{{ selectedNode.label }}</div>
              <div class="detail-content">
                <div v-if="selectedNode.description" class="detail-desc">
                  {{ selectedNode.description }}
                </div>
                <div class="detail-attrs">
                  <div v-for="attr in selectedNode.attributes" :key="attr.key" class="detail-attr">
                    <span class="attr-key">{{ attr.key }}：</span>
                    <span class="attr-value">{{ attr.value }}</span>
                  </div>
                </div>
              </div>
              <div class="detail-actions">
                <el-button size="small" type="primary" @click="viewNodeDetail">
                  查看详情
                </el-button>
              </div>
            </div>
          </div>

          <!-- 图例 -->
          <div class="graph-legend">
            <div class="legend-item">
              <span class="legend-dot" style="background: #1a3a6b;"></span>
              <span>问题</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background: #409eff;"></span>
              <span>法规</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background: #67c23a;"></span>
              <span>案例</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background: #e6a23c;"></span>
              <span>政策</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background: #f56c6c;"></span>
              <span>处罚</span>
            </div>
          </div>
        </el-card>

        <!-- 推理路径列表 -->
        <el-card class="path-card" v-if="messages.length > 0 && messages[messages.length - 1].reasoningChain">
          <template #header>
            <span>本次推理路径</span>
          </template>
          <el-steps direction="vertical" :space="60" size="small">
            <el-step
              v-for="(step, idx) in messages[messages.length - 1].reasoningChain"
              :key="idx"
              :title="step.query"
              :description="step.result"
            />
          </el-steps>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Delete, Promotion, Connection, Cpu, ArrowRight, Document, View,
  FullScreen, Refresh, Loading, Clock, Check, Close, Select, More, Sunrise
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import { graphApi } from '@/api'

const inputMessage = ref('')
const isThinking = ref(false)
const messages = ref([])
const chatMessagesRef = ref(null)
const showReasoning = ref(true)
const useNeo4j = ref(false)
const expandedSteps = ref([])
const selectedNode = ref(null)
const hoveredNodeId = ref(null)
const highlightedNodes = ref([])
const highlightedEdges = ref([])

// 图数据
const graphData = reactive({
  nodes: [],
  edges: []
})

const exampleQuestions = [
  '工地脚手架坠落事故如何处罚？',
  '施工许可证申请需要哪些前置条件？',
  '建设工程竣工验收流程是什么？'
]

// 增强的思考步骤 - 更详细的描述
const thinkingSteps = [
  { name: '理解问题', detail: '正在分析问题的关键实体和语义...' },
  { name: '知识检索', detail: '正在搜索相关的法规、案例和文件...' },
  { name: '图谱推理', detail: '正在构建实体间的关联关系...' },
  { name: '生成回答', detail: '正在综合信息生成最终答案...' }
]

// 趣味提示
const funTips = [
  '正在知识的海洋中遨游...',
  '让AI仔细思考一下这个问题...',
  '正在建立知识点之间的联系...',
  '这个问题有点意思，让我分析分析...',
  '调用脑细胞中...',
  '知识图谱构建ing...',
  '答案马上就到～',
  '正在调动专业知识库...'
]
const thinkingCurrent = ref(-1)
const thinkingProgress = ref(0)
const liveReasoningChain = ref([])
const currentTipIndex = ref(0)
let tipRotateTimer = null

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true
})

const renderMarkdown = (content) => {
  if (!content) return ''
  try {
    return marked.parse(content)
  } catch (e) {
    return content
  }
}

// 模拟图数据
const mockGraphData = {
  nodes: [
    { id: 'q1', label: '脚手架坠落事故', type: 'question', x: 200, y: 50, description: '工地脚手架搭建不符合规范导致坠落事故', attributes: [{ key: '事故类型', value: '安全事故' }, { key: '严重程度', value: '重大' }] },
    { id: 'n1', label: '安全生产管理条例', type: 'law', x: 80, y: 130, description: '建设工程安全生产管理条例', attributes: [{ key: '发文机关', value: '国务院' }, { key: '生效日期', value: '2004年2月1日' }] },
    { id: 'n2', label: '第78条', type: 'article', x: 200, y: 130, description: '施工单位未按规定设置安全防护设施的处罚规定', attributes: [{ key: '罚款范围', value: '5万-10万元' }, { key: '情节严重', value: '10万-20万元' }] },
    { id: 'n3', label: '2023年XX工地事故', type: 'case', x: 320, y: 130, description: '某工地脚手架坠落致2人死亡事故', attributes: [{ key: '发生时间', value: '2023年5月' }, { key: '处罚金额', value: '15万元' }] },
    { id: 'n4', label: 'JGJ59安全标准', type: 'standard', x: 80, y: 230, description: '建筑施工安全检查标准', attributes: [{ key: '标准编号', value: 'JGJ59-2011' }, { key: '性质', value: '强制性标准' }] },
    { id: 'n5', label: '行政处罚法', type: 'law', x: 200, y: 230, description: '中华人民共和国行政处罚法', attributes: [{ key: '发文机关', value: '全国人大' }, { key: '效力级别', value: '法律' }] },
    { id: 'n6', label: '罚款15万元', type: 'penalty', x: 320, y: 230, description: '依据安全生产管理条例第78条的处罚决定', attributes: [{ key: '处罚对象', value: '施工单位' }, { key: '执行状态', value: '已执行' }] }
  ],
  edges: [
    { id: 'e1', source: 'q1', target: 'n1', label: '涉及' },
    { id: 'e2', source: 'n1', target: 'n2', label: '包含' },
    { id: 'e3', source: 'n2', target: 'n6', label: '导致' },
    { id: 'e4', source: 'q1', target: 'n3', label: '类似案例' },
    { id: 'e5', source: 'n3', target: 'n6', label: '处罚依据' },
    { id: 'e6', source: 'n4', target: 'n2', label: '支撑' },
    { id: 'e7', source: 'n5', target: 'n6', label: '程序依据' }
  ]
}

// 模拟推理链数据
const mockReasoningChain = [
  {
    query: '脚手架坠落事故涉及哪些法规？',
    result: '涉及《建设工程安全生产管理条例》',
    entities: ['脚手架', '坠落', '事故', '安全', '生产']
  },
  {
    query: '查找相关处罚条款？',
    result: '《条例》第78条规定了处罚标准',
    entities: ['第78条', '处罚', '罚款']
  },
  {
    query: '查找类似案例？',
    result: '2023年XX工地事故与本案高度相似',
    entities: ['2023年', 'XX工地', '脚手架']
  },
  {
    query: '综合法规和案例生成最终答案？',
    result: '综合分析完成',
    entities: ['处罚', '15万元', '已执行']
  }
]

// 模拟回答数据
const mockAnswer = `
## 事故分析与处罚建议

### 一、事故定性
该脚手架坠落事故属于**安全生产责任事故**，根据《建设工程安全生产管理条例》相关规定，施工单位负主要责任。

### 二、法律依据

| 法规 | 条款 | 适用情形 |
|-----|-----|---------|
| 建设工程安全生产管理条例 | 第78条 | 未按规定设置安全防护设施 |
| 建筑施工安全检查标准 | JGJ59-2011 | 安全防护措施标准 |
| 行政处罚法 | 第32条 | 从轻或减轻情节 |

### 三、处罚标准

**一般情节**：罚款 **5-10万元**

**情节严重**（如造成人员伤亡）：罚款 **10-20万元**

### 四、类似案例参考

**2023年XX工地脚手架坠落事故**
- 事故原因：脚手架搭建不符合JGJ59标准
- 处罚结果：罚款15万元
- 借鉴意义：本案可参照此案例进行裁量

### 五、处置建议

1. **立即整改**：停工整改脚手架安全隐患
2. **责任追究**：追究项目经理和安全员责任
3. **行政处罚**：建议处以15万元罚款
`

const mockCitations = [
  { id: 'n1', type: 'law', typeName: '法规', title: '建设工程安全生产管理条例' },
  { id: 'n2', type: 'article', typeName: '条款', title: '第78条处罚规定' },
  { id: 'n3', type: 'case', typeName: '案例', title: '2023年XX工地事故' },
  { id: 'n5', type: 'law', typeName: '法规', title: '行政处罚法' }
]

// 根据问题动态生成图谱数据
const generateDynamicGraphData = (question, reasoningChain) => {
  const entities = reasoningChain.flatMap(step => step.entities || [])
  const knowledgeFound = reasoningChain.flatMap(step => step.details?.knowledge_found || [])

  const baseY = 50
  const nodeSpacing = 140
  const startX = 80

  // 动态生成节点
  const nodes = []
  const edges = []

  // 问题节点
  nodes.push({
    id: 'q1',
    label: question.length > 10 ? question.slice(0, 10) + '...' : question,
    type: 'question',
    x: 200,
    y: baseY,
    description: question,
    attributes: []
  })

  // 基于找到的知识生成节点
  const uniqueKnowledge = [...new Set(knowledgeFound.filter(k => k))].slice(0, 5)
  uniqueKnowledge.forEach((title, idx) => {
    const types = ['law', 'case', 'policy', 'article', 'standard']
    nodes.push({
      id: `n${idx + 1}`,
      label: title.length > 12 ? title.slice(0, 12) + '...' : title,
      type: types[idx % types.length],
      x: startX + (idx % 3) * nodeSpacing,
      y: baseY + Math.floor(idx / 3) * 120 + 100,
      description: `与"${question}"相关的知识`,
      attributes: [{ key: '来源', value: '知识库' }]
    })

    edges.push({
      id: `e${idx + 1}`,
      source: 'q1',
      target: `n${idx + 1}`,
      label: '涉及'
    })
  })

  // 基于实体生成额外节点
  const uniqueEntities = [...new Set(entities.filter(e => e))].slice(0, 4)
  uniqueEntities.forEach((entity, idx) => {
    const nodeId = `e${idx + 10}`
    nodes.push({
      id: nodeId,
      label: entity.length > 8 ? entity.slice(0, 8) + '...' : entity,
      type: 'policy',
      x: startX + 60 + (idx % 2) * 200,
      y: baseY + 280,
      description: `识别到的实体: ${entity}`,
      attributes: [{ key: '类型', value: '实体' }]
    })

    // 连接到最近的知识节点
    if (uniqueKnowledge.length > 0) {
      const targetIdx = idx % uniqueKnowledge.length
      edges.push({
        id: `ee${idx + 1}`,
        source: `n${targetIdx + 1}`,
        target: nodeId,
        label: '关联'
      })
    }
  })

  return { nodes, edges }
}

// 获取节点颜色
const getNodeColor = (type) => {
  const colors = {
    question: '#1a3a6b',
    law: '#409eff',
    article: '#409eff',
    case: '#67c23a',
    policy: '#e6a23c',
    penalty: '#f56c6c',
    standard: '#909399'
  }
  return colors[type] || '#909399'
}

// 获取节点图标
const getNodeIcon = (type) => {
  const icons = {
    question: '?',
    law: '法',
    article: '条',
    case: '案',
    policy: '策',
    penalty: '罚',
    standard: '标'
  }
  return icons[type] || '•'
}

// 获取节点类型名称
const getNodeTypeName = (type) => {
  const names = {
    question: '问题',
    law: '法规',
    article: '条款',
    case: '案例',
    policy: '政策',
    penalty: '处罚',
    standard: '标准'
  }
  return names[type] || '节点'
}

// 获取实体类型标签颜色
const getEntityType = (idx) => {
  const types = ['', 'primary', 'success', 'warning']
  return types[idx % types.length]
}

// 获取边的路径
const getEdgePath = (edge) => {
  const source = graphData.nodes.find(n => n.id === edge.source)
  const target = graphData.nodes.find(n => n.id === edge.target)
  if (!source || !target) return ''

  const dx = target.x - source.x
  const dy = target.y - source.y
  const dr = Math.sqrt(dx * dx + dy * dy) * 0.5

  return `M${source.x},${source.y} Q${(source.x + target.x) / 2},${(source.y + target.y) / 2 - 30} ${target.x},${target.y}`
}

// 选择节点
const selectNode = (node) => {
  selectedNode.value = node
  highlightedNodes.value = [node.id]
  // 高亮关联边
  const relatedEdges = graphData.edges.filter(e => e.source === node.id || e.target === node.id)
  highlightedEdges.value = relatedEdges.map(e => e.id)
}

// 悬停节点
const hoverNode = (nodeId) => {
  hoveredNodeId.value = nodeId
}

// 取消悬停
const unhoverNode = () => {
  hoveredNodeId.value = null
}

// 高亮边
const highlightEdge = (edge) => {
  highlightedEdges.value = [edge.id]
}

// 取消高亮边
const unhighlightEdge = () => {
  if (selectedNode.value) {
    const relatedEdges = graphData.edges.filter(e => e.source === selectedNode.value.id || e.target === selectedNode.value.id)
    highlightedEdges.value = relatedEdges.map(e => e.id)
  } else {
    highlightedEdges.value = []
  }
}

// 高亮引用节点
const highlightNode = (nodeId) => {
  const node = graphData.nodes.find(n => n.id === nodeId)
  if (node) {
    selectNode(node)
  }
}

// 切换推理步骤展开
const toggleStep = (stepIdx) => {
  const idx = expandedSteps.value.indexOf(stepIdx)
  if (idx > -1) {
    expandedSteps.value.splice(idx, 1)
  } else {
    expandedSteps.value.push(stepIdx)
  }
}

// 重置图谱
const resetGraph = () => {
  selectedNode.value = null
  highlightedNodes.value = []
  highlightedEdges.value = []
}

// 全屏切换
const toggleFullscreen = () => {
  ElMessage.info('全屏功能开发中')
}

// 查看节点详情
const viewNodeDetail = () => {
  if (selectedNode.value) {
    ElMessage.info(`跳转至：${selectedNode.value.label}`)
  }
}

// 清空历史
const clearHistory = () => {
  messages.value = []
  resetGraph()
}

// 思考动画 - 模拟进度 + 实时推理链
const REASONING_STEPS = [
  { query: '理解问题并识别关键实体', result: '正在分析问题的关键实体和语义...', entities: [] },
  { query: '检索相关知识库内容', result: '正在搜索相关的法规、案例和文件...', entities: [] },
  { query: '图谱推理与关联扩展', result: '正在构建实体间的关联关系...', entities: [] },
  { query: '综合知识生成最终回答', result: '正在整合信息生成答案...', entities: [] }
]

const startThinkingAnimation = () => {
  let progress = 0
  let stepIndex = 0
  liveReasoningChain.value = []
  currentTipIndex.value = 0

  // 立即显示第一条
  liveReasoningChain.value.push({ ...REASONING_STEPS[0] })

  const timer = setInterval(() => {
    progress += Math.random() * 15 + 5
    if (progress > 100) progress = 100
    thinkingProgress.value = Math.round(progress)

    // 根据进度更新当前步骤
    const totalSteps = REASONING_STEPS.length
    const stepThreshold = 100 / totalSteps
    stepIndex = Math.min(Math.floor(progress / stepThreshold), totalSteps - 1)
    thinkingCurrent.value = stepIndex

    // 更新推理链
    if (stepIndex < totalSteps) {
      // 更新最后一条的状态
      const lastIdx = liveReasoningChain.value.length - 1
      if (lastIdx >= 0) {
        liveReasoningChain.value[lastIdx] = {
          ...REASONING_STEPS[stepIndex],
          entities: stepIndex > 0 ? generateMockEntities(stepIndex) : []
        }
      }
      // 如果进入新步骤，添加新步骤
      if (stepIndex > lastIdx && stepIndex < totalSteps) {
        liveReasoningChain.value.push({ ...REASONING_STEPS[stepIndex] })
      }
    }

    // 轮换趣味提示
    if (Math.random() < 0.3) {
      currentTipIndex.value = (currentTipIndex.value + 1) % funTips.length
    }

    if (progress >= 100) {
      clearInterval(timer)
    }
  }, 300)
  return timer
}

// 生成模拟实体用于显示
const generateMockEntities = (stepIdx) => {
  const entitySets = [
    ['脚手架', '坠落事故', '安全施工'],
    ['安全生产管理条例', '第78条', '行政处罚法'],
    ['关联法规', '处罚标准', '裁量基准'],
    ['最终答案', '法律依据', '处罚建议']
  ]
  return entitySets[stepIdx] || []
}

// 发送消息
const handleSend = async () => {
  if (!inputMessage.value.trim()) return

  const userMsg = {
    role: 'user',
    content: inputMessage.value,
    time: new Date().toLocaleTimeString()
  }
  messages.value.push(userMsg)
  expandedSteps.value = []
  inputMessage.value = ''
  isThinking.value = true
  thinkingCurrent.value = 0
  thinkingProgress.value = 0
  liveReasoningChain.value = []

  // 启动进度动画
  const progressTimer = startThinkingAnimation()

  scrollToBottom()

  try {
    const result = await graphApi.qa(userMsg.content, useNeo4j.value)

    // 停止进度动画
    clearInterval(progressTimer)
    thinkingProgress.value = 100
    thinkingCurrent.value = thinkingSteps.length - 1

    // 更新图谱数据 - 使用API返回的数据或动态生成
    if (result.graph_data && result.graph_data.nodes && result.graph_data.nodes.length > 0) {
      graphData.nodes = result.graph_data.nodes
      graphData.edges = result.graph_data.edges
    } else {
      // 动态生成图谱数据
      const reasoningChain = result.reasoning_chain || liveReasoningChain.value
      const generatedGraph = generateDynamicGraphData(userMsg.content, reasoningChain)
      graphData.nodes = generatedGraph.nodes
      graphData.edges = generatedGraph.edges
    }
    highlightedNodes.value = []
    highlightedEdges.value = []

    isThinking.value = false
    thinkingCurrent.value = -1

    const aiMsg = {
      role: 'assistant',
      content: result.answer,
      reasoningChain: result.reasoning_chain || [],
      citations: result.citations || [],
      time: new Date().toLocaleTimeString()
    }
    messages.value.push(aiMsg)

  } catch (error) {
    console.error('图谱问答失败:', error)
    clearInterval(progressTimer)
    isThinking.value = false
    thinkingCurrent.value = -1
    ElMessage.error('问答服务出错，请稍后重试')

    // 保留用户消息，显示错误提示
    const aiMsg = {
      role: 'assistant',
      content: '抱歉，服务暂时不可用，请稍后重试。',
      reasoningChain: [],
      citations: [],
      time: new Date().toLocaleTimeString()
    }
    messages.value.push(aiMsg)
  }

  scrollToBottom()
}

// 示例问题
const askExample = (question) => {
  inputMessage.value = question
  handleSend()
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    chatMessagesRef.value?.scrollTo({
      top: chatMessagesRef.value.scrollHeight,
      behavior: 'smooth'
    })
  })
}

onMounted(() => {
  // 初始化图谱 - 延迟加载模拟数据
  setTimeout(() => {
    graphData.nodes = [...mockGraphData.nodes]
    graphData.edges = [...mockGraphData.edges]
  }, 500)
})

// 图谱数据变化的观察者 - 动态效果
import { watch } from 'vue'
let prevNodeCount = 0
let prevEdgeCount = 0

watch(() => graphData.nodes.length, (newLen) => {
  if (newLen > prevNodeCount && prevNodeCount > 0) {
    // 有新节点时添加动画标记
    nextTick(() => {
      document.querySelectorAll('.node-group').forEach((g, idx) => {
        if (idx >= prevNodeCount) {
          g.classList.add('new-node')
          setTimeout(() => g.classList.remove('new-node'), 600)
        }
      })
    })
  }
  prevNodeCount = newLen
})

watch(() => graphData.edges.length, (newLen) => {
  if (newLen > prevEdgeCount && prevEdgeCount > 0) {
    nextTick(() => {
      document.querySelectorAll('.edge-path').forEach((e, idx) => {
        if (idx >= prevEdgeCount) {
          e.classList.add('new-edge')
          setTimeout(() => e.classList.remove('new-edge'), 500)
        }
      })
    })
  }
  prevEdgeCount = newLen
})
</script>

<style scoped>
.graph-qa-page {
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

.chat-card,
.graph-card,
.path-card {
  margin-bottom: 16px;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.empty-graph {
  margin-bottom: 20px;
}

.example-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 16px;
}

.example-tag {
  cursor: pointer;
}

/* 消息样式 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  min-height: 300px;
  max-height: calc(100vh - 480px);
}

.chat-message {
  margin-bottom: 24px;
}

.message {
  display: flex;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 85%;
}

.message-header {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 13px;
}

.message.user .message-header {
  flex-direction: row-reverse;
}

.sender-name {
  font-weight: 600;
  color: #303133;
}

.message-time {
  color: #c0c4cc;
}

.message-body {
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.6;
}

.message.assistant .message-body {
  background: #fff;
  border: 1px solid #e4e7ed;
}

.message.user .message-body {
  background: #1a3a6b;
  color: #fff;
}

/* 推理过程 */
.reasoning-section {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.reasoning-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 12px;
}

.reasoning-steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reasoning-step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-query {
  color: #303133;
  font-weight: 500;
  font-size: 14px;
}

.step-result {
  color: #606266;
  font-size: 13px;
  margin-top: 4px;
}

.step-entities {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
}

.step-details {
  background: #fff;
  border-radius: 4px;
  padding: 12px;
  margin-top: 12px;
  font-size: 12px;
  border: 1px solid #e4e7ed;
}

.detail-item {
  margin-bottom: 8px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  color: #909399;
  font-weight: 500;
}

.detail-value {
  color: #303133;
}

.knowledge-list {
  margin-top: 6px;
  padding-left: 12px;
}

.knowledge-item {
  color: #606266;
  line-height: 1.8;
}

.reasoning-step {
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.reasoning-step:hover {
  background: #f5f7fa;
}

.reasoning-step.is-expanded {
  background: #f0f9ff;
}

.step-expand-icon {
  display: flex;
  align-items: center;
  color: #c0c4cc;
}

.step-expand-icon .el-icon {
  transition: transform 0.3s;
}

.step-expand-icon .el-icon.is-expanded {
  transform: rotate(90deg);
}

.step-arrow {
  color: #409eff;
  margin-top: 4px;
}

/* 引用 */
.citations {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.citations-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.citation-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.citation-item:hover {
  background: #e4e7ed;
}

.citation-title {
  flex: 1;
  font-size: 13px;
  color: #303133;
}

.citation-link {
  color: #409eff;
}

/* 思考中 */
.thinking {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px 0;
}

.thinking-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #667eea;
  font-weight: 600;
  min-width: 40px;
}

.thinking-steps {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.thinking-step {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #f5f7fa;
  color: #909399;
  font-size: 14px;
  transition: all 0.3s ease;
}

.thinking-step.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  color: #667eea;
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.thinking-step.completed {
  background: #f0f9f0;
  color: #67c23a;
}

.thinking-icon {
  width: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.check-icon {
  color: #67c23a;
}

.loading-icon {
  color: #667eea;
  animation: rotate 1s linear infinite;
}

.waiting-icon {
  color: #c0c4cc;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.step-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.step-name {
  font-weight: 500;
}

.step-detail {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}

.thinking-step.active .step-detail {
  color: #667eea;
  opacity: 0.8;
}

.fun-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #c0c4cc;
  padding: 8px 12px;
  background: #fdf6ec;
  border-radius: 6px;
  animation: fadeIn 0.5s ease;
}

.fun-tip .el-icon {
  color: #e6a23c;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

.thinking-mode {
  margin-left: 8px;
}

/* 实时推理链样式 */
.reasoning-section.thinking-reasoning {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.reasoning-section.thinking-reasoning .reasoning-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 16px;
}

.reasoning-progress-text {
  margin-left: auto;
  font-size: 12px;
  color: #909399;
  background: #fff;
  padding: 2px 8px;
  border-radius: 10px;
}

.reasoning-section.thinking-reasoning .reasoning-steps {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.reasoning-section.thinking-reasoning .reasoning-step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  position: relative;
  padding: 12px 0;
}

.reasoning-section.thinking-reasoning .step-indicator {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  z-index: 1;
}

.reasoning-section.thinking-reasoning .step-check {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #67c23a;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reasoning-section.thinking-reasoning .step-loading {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #667eea;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reasoning-section.thinking-reasoning .step-loading .el-icon {
  animation: rotate 1s linear infinite;
}

.reasoning-section.thinking-reasoning .step-content {
  flex: 1;
  min-width: 0;
}

.reasoning-section.thinking-reasoning .step-query {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.reasoning-section.thinking-reasoning .step-result {
  color: #606266;
  font-size: 13px;
  margin-top: 4px;
}

.reasoning-section.thinking-reasoning .step-result.is-calculating {
  color: #667eea;
}

.calc-dots {
  display: inline-block;
}

.calc-dots::after {
  content: '';
  animation: dots 1.5s infinite;
}

@keyframes dots {
  0%, 20% { content: ''; }
  40% { content: '.'; }
  60% { content: '..'; }
  80%, 100% { content: '...'; }
}

.reasoning-section.thinking-reasoning .step-entities {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
}

.reasoning-section.thinking-reasoning .step-connector {
  position: absolute;
  left: 11px;
  top: 36px;
  width: 2px;
  height: calc(100% - 12px);
  background: #e4e7ed;
}

.reasoning-section.thinking-reasoning .reasoning-step.is-active .step-connector {
  background: linear-gradient(to bottom, #667eea 0%, #e4e7ed 100%);
}

.reasoning-section.thinking-reasoning .reasoning-step.is-done .step-connector {
  background: #67c23a;
}

/* 输入区域 */
.chat-input {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.hint {
  color: #c0c4cc;
  font-size: 13px;
}

/* 图谱区域 */
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
  min-height: 400px;
}

.graph-container svg {
  display: block;
}

.node-group {
  cursor: pointer;
  transition: all 0.3s ease;
}

.node-group.new-node {
  animation: nodeAppear 0.6s ease forwards;
}

@keyframes nodeAppear {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.edge-path.new-edge {
  animation: edgeDraw 0.5s ease forwards;
}

@keyframes edgeDraw {
  0% {
    stroke-dasharray: 100;
    stroke-dashoffset: 100;
  }
  100% {
    stroke-dasharray: 100;
    stroke-dashoffset: 0;
  }
}

.node-circle {
  transition: all 0.3s;
}

.edge-path {
  transition: all 0.3s;
}

.edge-label {
  font-size: 10px;
  pointer-events: none;
}

/* 节点详情 */
.node-detail {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 200px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 12px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.detail-type {
  font-size: 12px;
  color: #409eff;
}

.detail-title {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
  margin-bottom: 8px;
}

.detail-desc {
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
}

.detail-attrs {
  font-size: 12px;
}

.detail-attr {
  margin-bottom: 4px;
}

.attr-key {
  color: #909399;
}

.attr-value {
  color: #303133;
}

.detail-actions {
  margin-top: 12px;
  text-align: right;
}

/* 图例 */
.graph-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 0 0 8px 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #606266;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

/* 推理路径卡片 */
.path-card :deep(.el-step__title) {
  font-size: 13px;
}

.path-card :deep(.el-step__description) {
  font-size: 12px;
}

/* 答案样式 */
.message-body.answer {
  background: #fff;
}

.message-body.answer :deep(h2) {
  font-size: 16px;
  margin: 0 0 12px 0;
  color: #1a3a6b;
}

.message-body.answer :deep(h3) {
  font-size: 14px;
  margin: 16px 0 8px 0;
  color: #303133;
}

.message-body.answer :deep(table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  margin: 8px 0;
}

.message-body.answer :deep(th),
.message-body.answer :deep(td) {
  border: 1px solid #e4e7ed;
  padding: 8px;
  text-align: left;
}

.message-body.answer :deep(th) {
  background: #f5f7fa;
  font-weight: 600;
}

.message-body.answer :deep(strong) {
  color: #f56c6c;
}
</style>
