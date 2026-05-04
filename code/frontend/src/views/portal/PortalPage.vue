<template>
  <div class="portal-page" v-loading="loading">
    <!-- 顶部区域 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div class="header-text">
            <h1 class="page-title">数据统计分析</h1>
            <p class="page-subtitle">实时掌握系统知识资产与用户活动状况</p>
          </div>
        </div>
        <div class="header-right">
          <div class="date-picker">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              :shortcuts="dateShortcuts"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="handleDateChange"
            />
          </div>
          <el-button type="primary" class="refresh-btn" @click="refreshData" :loading="refreshing">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-grid">
      <div class="stat-card" v-for="(stat, index) in statsCards" :key="index" :class="stat.type">
        <div class="stat-bg-effect"></div>
        <div class="stat-content">
          <div class="stat-header">
            <div class="stat-icon" :style="{ background: stat.iconBg }">
              <el-icon :style="{ color: stat.iconColor }">
                <component :is="stat.icon" />
              </el-icon>
            </div>
            <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
              <el-icon v-if="stat.trend > 0"><Top /></el-icon>
              <el-icon v-else><Bottom /></el-icon>
              <span>{{ Math.abs(stat.trend) }}%</span>
            </div>
          </div>
          <div class="stat-value">{{ stat.value.toLocaleString() }}</div>
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-progress" v-if="stat.progress !== undefined">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: stat.progress + '%', background: stat.iconColor }"></div>
            </div>
            <span class="progress-text">{{ stat.progress }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 知识增长趋势 -->
      <div class="chart-card trend-chart">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"/>
              </svg>
            </span>
            <h3>知识增长趋势</h3>
          </div>
          <div class="chart-actions">
            <el-radio-group v-model="trendPeriod" size="small" @change="updateTrendChart">
              <el-radio-button label="week">本周</el-radio-button>
              <el-radio-button label="month">本月</el-radio-button>
              <el-radio-button label="year">本年</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div class="chart-body">
          <div ref="trendChartRef" class="chart-container"></div>
        </div>
      </div>

      <!-- 分类分布 -->
      <div class="chart-card category-chart">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 2a10 10 0 0 1 10 10"/>
                <path d="M12 12L12 2"/>
                <path d="M12 12L20.5 7"/>
              </svg>
            </span>
            <h3>分类分布</h3>
          </div>
          <div class="chart-actions">
            <el-radio-group v-model="categoryType" size="small" @change="updateCategoryChart">
              <el-radio-button label="pie">环形图</el-radio-button>
              <el-radio-button label="rose">玫瑰图</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div class="chart-body">
          <div ref="categoryChartRef" class="chart-container"></div>
        </div>
      </div>

      <!-- 索引状态分布 -->
      <div class="chart-card status-chart">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <path d="M3 9h18"/>
                <path d="M9 21V9"/>
              </svg>
            </span>
            <h3>索引状态分布</h3>
          </div>
        </div>
        <div class="chart-body">
          <div ref="statusChartRef" class="chart-container"></div>
        </div>
      </div>

      <!-- 热门标签 TOP15 -->
      <div class="chart-card tags-chart">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>
                <line x1="7" y1="7" x2="7.01" y2="7"/>
              </svg>
            </span>
            <h3>热门标签 TOP15</h3>
          </div>
          <div class="chart-actions">
            <el-radio-group v-model="tagsType" size="small" @change="updateTagsChart">
              <el-radio-button label="bar">柱状图</el-radio-button>
              <el-radio-button label="word">词云</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div class="chart-body">
          <div ref="tagsChartRef" class="chart-container"></div>
        </div>
      </div>

      <!-- 知识来源 TOP10 -->
      <div class="chart-card source-chart">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14,2 14,8 20,8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
            </span>
            <h3>知识来源 TOP10</h3>
          </div>
        </div>
        <div class="chart-body">
          <div ref="sourceChartRef" class="chart-container"></div>
        </div>
      </div>

      <!-- 用户活跃度趋势 -->
      <div class="chart-card activity-chart">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </span>
            <h3>用户活跃度趋势</h3>
          </div>
        </div>
        <div class="chart-body">
          <div ref="activityChartRef" class="chart-container"></div>
        </div>
      </div>
    </div>

    <!-- 底部区域 -->
    <div class="bottom-grid">
      <!-- 快捷操作 -->
      <div class="quick-actions-card">
        <div class="card-header">
          <h3>快捷操作</h3>
          <span class="card-subtitle">常用功能快速入口</span>
        </div>
        <div class="quick-actions">
          <div class="action-item" v-for="(action, index) in quickActions" :key="index" @click="handleAction(action)">
            <div class="action-icon" :style="{ background: action.iconBg, color: action.iconColor }">
              <el-icon><component :is="action.icon" /></el-icon>
            </div>
            <span class="action-label">{{ action.label }}</span>
            <span class="action-desc">{{ action.desc }}</span>
          </div>
        </div>
      </div>

      <!-- 最近动态 + 索引进度 -->
      <div class="right-column">
        <!-- 最近动态 -->
        <div class="activity-card">
          <div class="card-header">
            <h3>最近动态</h3>
            <el-button link type="primary" @click="loadMoreActivity">查看更多</el-button>
          </div>
          <div class="activity-timeline">
            <div v-for="(item, index) in recentActivity" :key="index" class="timeline-item">
              <div class="timeline-marker" :class="item.type"></div>
              <div class="timeline-content">
                <div class="timeline-header">
                  <span class="timeline-title">{{ item.title }}</span>
                  <span class="timeline-time">{{ item.time }}</span>
                </div>
                <div class="timeline-desc">{{ item.description }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 实时索引进度 -->
        <div class="progress-card">
          <div class="card-header">
            <h3>实时索引进度</h3>
            <el-tag size="small" type="success" effect="light">
              <el-icon class="is-loading"><Loading /></el-icon>
              进行中
            </el-tag>
          </div>
          <div class="progress-list">
            <div v-for="(item, index) in indexProgress" :key="index" class="progress-item">
              <div class="progress-info">
                <span class="progress-name">{{ item.name }}</span>
                <span class="progress-count">{{ item.current }}/{{ item.total }}</span>
              </div>
              <el-progress
                :percentage="item.percentage"
                :stroke-width="8"
                :color="item.color"
                :show-text="false"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  Refresh, Top, Bottom, Loading,
  Upload, Edit, Search, Share, ChatDotRound, List,
  Document, User, Connection, Grid, Clock
} from '@element-plus/icons-vue'
import { knowledgeApi } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 状态
const refreshing = ref(false)
const loading = ref(true)
const trendPeriod = ref('month')
const categoryType = ref('pie')
const tagsType = ref('bar')

// 门户数据
const portalData = ref({
  total: 0,
  monthly_new: 0,
  es_indexed: 0,
  vector_indexed: 0,
  graph_nodes: 0,
  user_count: 0,
  categories: [],
  tags: [],
  sources: [],
  trend: [],
  index_status: []
})

// 日期范围
const dateRange = ref([])
const dateShortcuts = [
  { text: '最近7天', value: () => {
    const end = new Date()
    const start = new Date()
    start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
    return [start, end]
  }},
  { text: '最近30天', value: () => {
    const end = new Date()
    const start = new Date()
    start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
    return [start, end]
  }},
  { text: '最近90天', value: () => {
    const end = new Date()
    const start = new Date()
    start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
    return [start, end]
  }}
]

// 统计数据卡片
const statsCards = reactive([
  {
    type: 'total',
    icon: markRaw(Document),
    iconBg: 'linear-gradient(135deg, #667eea20, #764ba220)',
    iconColor: '#667eea',
    value: 0,
    label: '知识总数',
    trend: 0,
    progress: undefined
  },
  {
    type: 'monthly',
    icon: markRaw(List),
    iconBg: 'linear-gradient(135deg, #f59e0b20, #d9770620)',
    iconColor: '#f59e0b',
    value: 0,
    label: '本月新增',
    trend: 0,
    progress: undefined
  },
  {
    type: 'es',
    icon: markRaw(Search),
    iconBg: 'linear-gradient(135deg, #10b98120, #05966920)',
    iconColor: '#10b981',
    value: 0,
    label: '全文索引量',
    trend: 0,
    progress: undefined
  },
  {
    type: 'vector',
    icon: markRaw(Connection),
    iconBg: 'linear-gradient(135deg, #3b82f620, #2563eb20)',
    iconColor: '#3b82f6',
    value: 0,
    label: '向量索引量',
    trend: 0,
    progress: undefined
  },
  {
    type: 'graph',
    icon: markRaw(Grid),
    iconBg: 'linear-gradient(135deg, #8b5cf620, #7c3aed20)',
    iconColor: '#8b5cf6',
    value: 0,
    label: '图谱节点数',
    trend: 0,
    progress: undefined
  },
  {
    type: 'users',
    icon: markRaw(User),
    iconBg: 'linear-gradient(135deg, #ec489920, #db277720)',
    iconColor: '#ec4899',
    value: 0,
    label: '用户总数',
    trend: 0,
    progress: undefined
  }
])

// 更新统计卡片
const updateStatsCards = () => {
  statsCards[0].value = portalData.value.total || 0
  statsCards[1].value = portalData.value.monthly_new || 0
  statsCards[2].value = portalData.value.es_indexed || 0
  if (portalData.value.total > 0) {
    statsCards[2].progress = Math.round((portalData.value.es_indexed / portalData.value.total) * 100)
  }
  statsCards[3].value = portalData.value.vector_indexed || 0
  if (portalData.value.total > 0) {
    statsCards[3].progress = Math.round((portalData.value.vector_indexed / portalData.value.total) * 100)
  }
  statsCards[4].value = portalData.value.graph_nodes || 0
  if (portalData.value.total > 0) {
    statsCards[4].progress = Math.round((portalData.value.graph_nodes / portalData.value.total) * 100)
  }
  statsCards[5].value = portalData.value.user_count || 0
}

// 加载门户数据
const loadPortalStats = async () => {
  try {
    loading.value = true
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.date_from = dateRange.value[0]
      params.date_to = dateRange.value[1]
    }
    const [statsRes, activitiesRes, progressRes] = await Promise.all([
      knowledgeApi.portalStats(params),
      knowledgeApi.recentActivities(10),
      knowledgeApi.indexProgress()
    ])
    portalData.value = statsRes
    recentActivity.value = activitiesRes
    // 清空并重新填充 indexProgress
    indexProgress.splice(0, indexProgress.length, ...progressRes)
    updateStatsCards()
    updateCharts()
  } catch (error) {
    console.error('加载门户数据失败', error)
  } finally {
    loading.value = false
  }
}

// 快捷操作
const quickActions = [
  { icon: markRaw(Upload), label: '上传文档', desc: '支持PDF/Word', iconBg: 'linear-gradient(135deg, #667eea, #764ba2)', iconColor: '#fff', path: '/knowledge/manage-new?action=upload' },
  { icon: markRaw(Edit), label: '添加文本', desc: '富文本编辑', iconBg: 'linear-gradient(135deg, #10b981, #059669)', iconColor: '#fff', path: '/knowledge/manage-new?action=text' },
  { icon: markRaw(Search), label: '搜索知识', desc: '全文检索', iconBg: 'linear-gradient(135deg, #f59e0b, #d97706)', iconColor: '#fff', path: '/knowledge/search' },
  { icon: markRaw(Share), label: '查看图谱', desc: '知识关系', iconBg: 'linear-gradient(135deg, #3b82f6, #2563eb)', iconColor: '#fff', path: '/knowledge/graph' },
  { icon: markRaw(ChatDotRound), label: '智能助手', desc: 'AI问答', iconBg: 'linear-gradient(135deg, #8b5cf6, #7c3aed)', iconColor: '#fff', path: '/assistant/law' },
  { icon: markRaw(Refresh), label: '同步状态', desc: '刷新索引', iconBg: 'linear-gradient(135deg, #06b6d4, #0891b2)', iconColor: '#fff', path: null }
]

// 最近动态
const recentActivity = ref([
  { type: 'upload', title: '上传《建筑施工安全规范》', description: '法规分类 · PDF格式 · 2.3MB', time: '5分钟前' },
  { type: 'create', title: '新增分类"行业标准"', description: '属于政策法规大类', time: '15分钟前' },
  { type: 'update', title: '更新文档《消防法》', description: '更新摘要和标签', time: '30分钟前' },
  { type: 'upload', title: '上传《施工现场管理条例》', description: '制度分类 · DOC格式', time: '1小时前' },
  { type: 'graph', title: '创建知识图谱节点', description: '新增法规关系节点', time: '2小时前' },
  { type: 'search', title: '执行全文检索', description: '关键词: 施工安全', time: '3小时前' }
])

// 索引进度
const indexProgress = reactive([
  { name: '全文索引', current: 11520, total: 12856, percentage: 89.6, color: '#10b981' },
  { name: '向量索引', current: 8960, total: 12856, percentage: 69.7, color: '#3b82f6' },
  { name: '知识图谱', current: 4528, total: 12856, percentage: 35.2, color: '#8b5cf6' }
])

// 图表实例
let trendChart = null
let categoryChart = null
let statusChart = null
let tagsChart = null
let sourceChart = null
let activityChart = null

// DOM引用
const trendChartRef = ref(null)
const categoryChartRef = ref(null)
const statusChartRef = ref(null)
const tagsChartRef = ref(null)
const sourceChartRef = ref(null)
const activityChartRef = ref(null)

// 初始化所有图表
const initCharts = () => {
  try {
    initTrendChart()
    initCategoryChart()
    initStatusChart()
    initTagsChart()
    initSourceChart()
    initActivityChart()
  } catch (e) {
    console.error('初始化图表失败:', e)
  }
}

// 知识增长趋势图
const initTrendChart = () => {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)

  // 优先使用真实数据，否则使用占位数据
  const hasRealData = portalData.value.trend?.length > 0

  const periodData = {
    week: {
      labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      newData: hasRealData ? portalData.value.trend.slice(-7).map(item => item.new_count) : [12, 18, 15, 22, 28, 35, 42],
      indexData: hasRealData ? portalData.value.trend.slice(-7).map(item => item.index_count) : [10, 15, 13, 20, 26, 32, 38]
    },
    month: {
      labels: hasRealData ? portalData.value.trend.map(item => item.date.slice(5)) : ['第1周', '第2周', '第3周', '第4周'],
      newData: hasRealData ? portalData.value.trend.map(item => item.new_count) : [85, 120, 150, 180],
      indexData: hasRealData ? portalData.value.trend.map(item => item.index_count) : [75, 100, 130, 160]
    },
    year: {
      labels: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
      newData: hasRealData ? portalData.value.trend.map(item => item.new_count) : [320, 450, 380, 520, 680, 750, 820, 780, 900, 1050, 980, 1120],
      indexData: hasRealData ? portalData.value.trend.map(item => item.index_count) : [280, 380, 320, 460, 580, 650, 720, 680, 800, 920, 860, 1000]
    }
  }

  const current = periodData[trendPeriod.value]

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(102, 126, 234, 0.3)',
      borderWidth: 1,
      textStyle: { color: '#334155' },
      axisPointer: {
        type: 'cross',
        label: { backgroundColor: '#667eea' }
      },
      formatter: function(params) {
        let result = `<div style="font-weight:600;margin-bottom:8px">${params[0].axisValue}</div>`
        params.forEach(item => {
          result += `<div style="display:flex;align-items:center;gap:8px;margin:4px 0">
            <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${item.color}"></span>
            <span>${item.seriesName}:</span>
            <span style="font-weight:600">${item.value}</span>
          </div>`
        })
        return result
      }
    },
    legend: {
      data: ['新增知识', '索引完成'],
      bottom: 0,
      textStyle: { color: '#64748b', fontSize: 12 },
      itemGap: 24
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '18%',
      top: '8%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: current.labels,
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#64748b', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: '#64748b', fontSize: 11 },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }
    },
    series: [
      {
        name: '新增知识',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: '#667eea' },
        itemStyle: { color: '#667eea', borderColor: '#fff', borderWidth: 2 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(102, 126, 234, 0.35)' },
              { offset: 1, color: 'rgba(102, 126, 234, 0.02)' }
            ]
          }
        },
        data: current.newData,
        emphasis: {
          focus: 'series',
          itemStyle: { shadowBlur: 10, shadowColor: 'rgba(102, 126, 234, 0.3)' }
        }
      },
      {
        name: '索引完成',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: '#10b981' },
        itemStyle: { color: '#10b981', borderColor: '#fff', borderWidth: 2 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(16, 185, 129, 0.35)' },
              { offset: 1, color: 'rgba(16, 185, 129, 0.02)' }
            ]
          }
        },
        data: current.indexData,
        emphasis: {
          focus: 'series',
          itemStyle: { shadowBlur: 10, shadowColor: 'rgba(16, 185, 129, 0.3)' }
        }
      }
    ]
  }

  trendChart.setOption(option)
}

// 分类分布图
const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  categoryChart = echarts.init(categoryChartRef.value)

  const categoryColors = [
    ['#667eea', '#764ba2'],
    ['#10b981', '#059669'],
    ['#f59e0b', '#d97706'],
    ['#ec4899', '#db2777'],
    ['#8b5cf6', '#7c3aed']
  ]

  const categoryData = (portalData.value.categories || []).map((cat, index) => {
    const colorPair = categoryColors[index % categoryColors.length]
    return {
      value: cat.count,
      name: cat.category_name,
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: colorPair[0] },
            { offset: 1, color: colorPair[1] }
          ]
        }
      }
    }
  })

  if (!categoryData.length) {
    categoryData.push({ value: 1, name: '暂无数据', itemStyle: { color: '#e2e8f0' } })
  }

  const option = categoryType.value === 'rose' ? {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(102, 126, 234, 0.3)',
      textStyle: { color: '#334155' },
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '3%',
      top: 'center',
      textStyle: { color: '#64748b', fontSize: 11 },
      itemGap: 12
    },
    series: [{
      type: 'pie',
      radius: ['20%', '70%'],
      center: ['35%', '50%'],
      roseType: 'area',
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#334155' }
      },
      data: categoryData
    }]
  } : {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(102, 126, 234, 0.3)',
      textStyle: { color: '#334155' },
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '3%',
      top: 'center',
      textStyle: { color: '#64748b', fontSize: 11 },
      itemGap: 12
    },
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#334155' }
      },
      data: categoryData
    }]
  }

  categoryChart.setOption(option)
}

// 索引状态分布
const initStatusChart = () => {
  if (!statusChartRef.value) return
  statusChart = echarts.init(statusChartRef.value)

  const indexData = portalData.value.index_status || []
  const categories = indexData.map(s => s.category_name)
  const completedData = indexData.map(s => s.completed)
  const inProgressData = indexData.map(s => s.in_progress)
  const pendingData = indexData.map(s => s.pending)
  const failedData = indexData.map(s => s.failed)

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(102, 126, 234, 0.3)',
      textStyle: { color: '#334155' },
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['已完成', '进行中', '待处理', '失败'],
      bottom: 0,
      textStyle: { color: '#64748b', fontSize: 11 },
      itemGap: 16
    },
    grid: { left: '3%', right: '4%', bottom: '18%', top: '8%', containLabel: true },
    xAxis: {
      type: 'category',
      data: categories.length ? categories : ['无数据'],
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#64748b', fontSize: 11, rotate: 15 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: '#64748b', fontSize: 11 },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }
    },
    series: [
      {
        name: '已完成',
        type: 'bar',
        stack: 'total',
        barWidth: '50%',
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#10b981' },
              { offset: 1, color: '#34d399' }
            ]
          },
          borderRadius: [0, 0, 0, 0]
        },
        data: completedData.length ? completedData : [0]
      },
      {
        name: '进行中',
        type: 'bar',
        stack: 'total',
        barWidth: '50%',
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#667eea' },
              { offset: 1, color: '#818cf8' }
            ]
          }
        },
        data: inProgressData.length ? inProgressData : [0]
      },
      {
        name: '待处理',
        type: 'bar',
        stack: 'total',
        barWidth: '50%',
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#f59e0b' },
              { offset: 1, color: '#fbbf24' }
            ]
          }
        },
        data: pendingData.length ? pendingData : [0]
      },
      {
        name: '失败',
        type: 'bar',
        stack: 'total',
        barWidth: '50%',
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#ef4444' },
              { offset: 1, color: '#f87171' }
            ]
          },
          borderRadius: [4, 4, 0, 0]
        },
        data: failedData.length ? failedData : [0]
      }
    ]
  }

  statusChart.setOption(option)
}

// 热门标签图
const initTagsChart = () => {
  if (!tagsChartRef.value) return
  tagsChart = echarts.init(tagsChartRef.value)

  if (tagsType.value === 'word') {
    const tagsData = (portalData.value.tags || []).map(tag => ({
      name: tag.tag,
      value: tag.count
    }))

    if (!tagsData.length) {
      tagsData.push({ name: '暂无数据', value: 1 })
    }

    const option = {
      tooltip: {
        show: true,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: 'rgba(102, 126, 234, 0.3)',
        textStyle: { color: '#334155' },
        formatter: '{b}: {c}次'
      },
      series: [{
        type: 'wordCloud',
        shape: 'circle',
        left: 'center',
        top: 'center',
        width: '90%',
        height: '90%',
        sizeRange: [12, 48],
        rotationRange: [-45, 45],
        rotationStep: 15,
        gridSize: 8,
        drawOutOfBound: false,
        textStyle: {
          fontFamily: 'sans-serif',
          fontWeight: 'bold',
          color: function() {
            const colors = ['#667eea', '#764ba2', '#10b981', '#f59e0b', '#ec4899', '#3b82f6', '#8b5cf6', '#ef4444']
            return colors[Math.floor(Math.random() * colors.length)]
          }
        },
        emphasis: {
          textStyle: {
            shadowBlur: 10,
            shadowColor: '#333'
          }
        },
        data: tagsData
      }]
    }

    tagsChart.setOption(option)
  } else {
    const tagsBarData = (portalData.value.tags || []).map(tag => ({
      name: tag.tag,
      value: tag.count
    })).reverse()

    if (!tagsBarData.length) {
      tagsBarData.push({ name: '暂无数据', value: 0 })
    }

    const option = {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: 'rgba(102, 126, 234, 0.3)',
        textStyle: { color: '#334155' },
        axisPointer: { type: 'shadow' },
        formatter: '{b}: {c}次'
      },
      grid: { left: '3%', right: '12%', bottom: '3%', top: '3%', containLabel: true },
      xAxis: {
        type: 'value',
        axisLine: { show: false },
        axisLabel: { color: '#64748b', fontSize: 10 },
        splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }
      },
      yAxis: {
        type: 'category',
        data: tagsBarData.map(t => t.name),
        axisLine: { show: false },
        axisLabel: { color: '#64748b', fontSize: 10 }
      },
      series: [{
        type: 'bar',
        data: tagsBarData.map(t => t.value),
        barWidth: '50%',
        itemStyle: {
          borderRadius: [0, 4, 4, 0],
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: '#764ba2' },
              { offset: 0.5, color: '#667eea' },
              { offset: 1, color: '#3b82f6' }
            ]
          }
        },
        label: { show: true, position: 'right', color: '#64748b', fontSize: 10, formatter: '{c}' }
      }]
    }

    tagsChart.setOption(option)
  }
}

// 知识来源TOP10
const initSourceChart = () => {
  if (!sourceChartRef.value) return
  sourceChart = echarts.init(sourceChartRef.value)

  const sourceData = (portalData.value.sources || []).map(s => ({
    name: s.source,
    value: s.count
  })).reverse()

  if (!sourceData.length) {
    sourceData.push({ name: '暂无数据', value: 0 })
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(102, 126, 234, 0.3)',
      textStyle: { color: '#334155' },
      axisPointer: { type: 'shadow' },
      formatter: '{b}: {c}条'
    },
    grid: { left: '3%', right: '8%', bottom: '3%', top: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: '#64748b', fontSize: 10 },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }
    },
    yAxis: {
      type: 'category',
      data: sourceData.map(s => s.name),
      axisLine: { show: false },
      axisLabel: { color: '#64748b', fontSize: 10 }
    },
    series: [{
      type: 'bar',
      data: sourceData.map(s => s.value),
      barWidth: '55%',
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: function(params) {
          const colors = ['#667eea', '#764ba2', '#10b981', '#f59e0b', '#ec4899', '#3b82f6', '#8b5cf6', '#ef4444', '#06b6d4', '#84cc16']
          return colors[params.dataIndex % colors.length]
        }
      },
      label: { show: true, position: 'top', color: '#64748b', fontSize: 9, formatter: '{c}' }
    }]
  }

  sourceChart.setOption(option)
}

// 用户活跃度热力图
const initActivityChart = () => {
  if (!activityChartRef.value) return
  activityChart = echarts.init(activityChartRef.value)

  // 生成模拟数据
  const generateHeatmapData = () => {
    const data = []
    const hours = ['8:00', '9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00']
    const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

    for (let i = 0; i < days.length; i++) {
      for (let j = 0; j < hours.length; j++) {
        let value
        if (days[i] === '周六' || days[i] === '周日') {
          value = Math.floor(Math.random() * 30) + 10
        } else {
          if (j >= 2 && j <= 4) value = Math.floor(Math.random() * 80) + 60
          else if (j >= 9 && j <= 11) value = Math.floor(Math.random() * 70) + 40
          else value = Math.floor(Math.random() * 40) + 20
        }
        data.push([j, i, value])
      }
    }
    return { data, hours, days }
  }

  const { data, hours, days } = generateHeatmapData()

  const option = {
    tooltip: {
      position: 'top',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(102, 126, 234, 0.3)',
      textStyle: { color: '#334155' },
      formatter: function(params) {
        return `${days[params.value[1]]} ${hours[params.value[0]]}<br/>活跃用户: <strong>${params.value[2]}</strong>人`
      }
    },
    grid: { left: '3%', right: '8%', bottom: '15%', top: '5%', containLabel: true },
    xAxis: {
      type: 'category',
      data: hours,
      splitArea: { show: false },
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#64748b', fontSize: 9 }
    },
    yAxis: {
      type: 'category',
      data: days,
      splitArea: { show: false },
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#64748b', fontSize: 10 }
    },
    visualMap: {
      min: 0,
      max: 150,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '3%',
      inRange: {
        color: ['#f0f4ff', '#c7d2fe', '#a5b4fc', '#818cf8', '#667eea', '#5b63d4', '#4f46e5']
      },
      textStyle: { color: '#64748b', fontSize: 10 }
    },
    series: [{
      type: 'heatmap',
      data: data,
      label: { show: false },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.2)'
        }
      },
      itemStyle: {
        borderRadius: 3,
        borderColor: '#fff',
        borderWidth: 1
      }
    }]
  }

  activityChart.setOption(option)
}

// 更新图表（使用真实数据）
const updateCharts = () => {
  updateTrendChart()
  updateCategoryChart()
  updateStatusChart()
  updateTagsChart()
  updateSourceChart()
  updateActivityChart()
}

// 更新趋势图
const updateTrendChart = () => {
  if (trendChart) {
    const hasData = portalData.value.trend?.length > 0
    if (hasData) {
      // 重新初始化图表以确保渐变等配置正确应用
      initTrendChart()
    }
  }
}

// 更新分类图
const updateCategoryChart = () => {
  if (categoryChart && portalData.value.categories?.length) {
    categoryChart.dispose()
    initCategoryChart()
  }
}

// 更新状态图
const updateStatusChart = () => {
  if (statusChart && portalData.value.index_status?.length) {
    statusChart.dispose()
    initStatusChart()
  }
}

// 更新标签图
const updateTagsChart = () => {
  if (tagsChart && portalData.value.tags?.length) {
    tagsChart.dispose()
    initTagsChart()
  }
}

// 更新来源图
const updateSourceChart = () => {
  if (sourceChart && portalData.value.sources?.length) {
    sourceChart.dispose()
    initSourceChart()
  }
}

// 刷新数据
const refreshData = async () => {
  refreshing.value = true
  await loadPortalStats()
  refreshing.value = false
}

// 日期变化
const handleDateChange = () => {
  loadPortalStats()
}

// 加载更多动态
const loadMoreActivity = () => {
  router.push('/activity')
}

// 处理快捷操作
const handleAction = (action) => {
  if (action.path) {
    router.push(action.path)
  } else {
    refreshData()
  }
}

// 窗口大小变化时重绘图表
const handleResize = () => {
  trendChart?.resize()
  categoryChart?.resize()
  statusChart?.resize()
  tagsChart?.resize()
  sourceChart?.resize()
  activityChart?.resize()
}

// 生命周期
onMounted(() => {
  nextTick(() => {
    initCharts()
    loadPortalStats().catch(err => {
      console.error('加载门户数据失败:', err)
      ElMessage.error('加载统计数据失败，请刷新页面重试')
    })
  })
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  categoryChart?.dispose()
  statusChart?.dispose()
  tagsChart?.dispose()
  sourceChart?.dispose()
  activityChart?.dispose()
})
</script>

<style scoped>
.portal-page {
  padding: 0;
  animation: fadeIn 0.4s ease;
  background: linear-gradient(180deg, #f8fafc 0%, #fff 100%);
  min-height: 100vh;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 顶部区域 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #8b5cf6 100%);
  padding: 24px 28px;
  margin-bottom: 24px;
  border-radius: 0 0 24px 24px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  width: 52px;
  height: 52px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.logo-icon svg {
  width: 28px;
  height: 28px;
  color: #fff;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.page-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
  margin: 4px 0 0 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.date-picker :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  backdrop-filter: blur(10px);
  box-shadow: none;
}

.date-picker :deep(.el-input__inner) {
  color: #fff;
}

.date-picker :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.7);
}

.date-picker :deep(.el-input__prefix) {
  color: rgba(255, 255, 255, 0.8);
}

.date-picker :deep(.el-range-input) {
  color: #fff;
}

.date-picker :deep(.el-range-input::placeholder) {
  color: rgba(255, 255, 255, 0.6);
}

.date-picker :deep(.el-range-separator) {
  color: rgba(255, 255, 255, 0.7);
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  backdrop-filter: blur(10px);
  color: #fff;
  font-weight: 500;
  padding: 10px 20px;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  padding: 0 24px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  border-radius: 16px 16px 0 0;
}

.stat-card.total::before { background: linear-gradient(90deg, #667eea, #764ba2); }
.stat-card.monthly::before { background: linear-gradient(90deg, #f59e0b, #d97706); }
.stat-card.es::before { background: linear-gradient(90deg, #10b981, #059669); }
.stat-card.vector::before { background: linear-gradient(90deg, #3b82f6, #2563eb); }
.stat-card.graph::before { background: linear-gradient(90deg, #8b5cf6, #7c3aed); }
.stat-card.users::before { background: linear-gradient(90deg, #ec4899, #db2777); }

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
  border-color: transparent;
}

.stat-bg-effect {
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.03) 0%, transparent 70%);
  pointer-events: none;
}

.stat-content {
  position: relative;
  z-index: 1;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-icon .el-icon {
  font-size: 22px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 20px;
}

.stat-trend.up {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.stat-trend.down {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
}

.stat-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s ease;
}

.progress-text {
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  min-width: 36px;
}

/* 图表区域 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  padding: 0 24px;
  margin-bottom: 24px;
}

.chart-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.04);
  overflow: hidden;
  transition: all 0.3s ease;
}

.chart-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
}

.trend-chart {
  grid-column: span 3;
}

.chart-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #667eea15, #764ba215);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.title-icon svg {
  width: 16px;
  height: 16px;
  color: #667eea;
}

.chart-title h3 {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.chart-actions :deep(.el-radio-button__inner) {
  border-radius: 6px;
  font-size: 12px;
  padding: 5px 12px;
}

.chart-actions :deep(.el-radio-button:first-child .el-radio-button__inner) {
  border-radius: 6px;
}

.chart-body {
  padding: 16px;
}

.chart-container {
  height: 260px;
}

.trend-chart .chart-container {
  height: 280px;
}

/* 底部区域 */
.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 20px;
  padding: 0 24px 24px;
}

/* 快捷操作 */
.quick-actions-card,
.activity-card,
.progress-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.card-subtitle {
  font-size: 12px;
  color: #94a3b8;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 16px 20px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  border-radius: 12px;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
  overflow: hidden;
}

.action-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.action-item:hover::before {
  opacity: 1;
}

.action-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  position: relative;
  z-index: 1;
}

.action-icon .el-icon {
  font-size: 24px;
}

.action-label {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  position: relative;
  z-index: 1;
}

.action-desc {
  font-size: 11px;
  color: #94a3b8;
  position: relative;
  z-index: 1;
}

/* 最近动态 */
.right-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.activity-card .card-header {
  border-bottom: none;
  padding-bottom: 8px;
}

.activity-timeline {
  padding: 0 20px 16px;
}

.timeline-item {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px dashed #f1f5f9;
  position: relative;
}

.timeline-item:last-child {
  border-bottom: none;
}

.timeline-marker {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
  position: relative;
}

.timeline-marker::after {
  content: '';
  position: absolute;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  width: 1px;
  height: calc(100% + 12px);
  background: #e2e8f0;
}

.timeline-item:last-child .timeline-marker::after {
  display: none;
}

.timeline-marker.upload { background: linear-gradient(135deg, #667eea, #764ba2); }
.timeline-marker.create { background: linear-gradient(135deg, #10b981, #059669); }
.timeline-marker.update { background: linear-gradient(135deg, #f59e0b, #d97706); }
.timeline-marker.graph { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.timeline-marker.search { background: linear-gradient(135deg, #3b82f6, #2563eb); }

.timeline-content {
  flex: 1;
  min-width: 0;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.timeline-title {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.timeline-time {
  font-size: 11px;
  color: #94a3b8;
  flex-shrink: 0;
}

.timeline-desc {
  font-size: 12px;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 索引进度 */
.progress-card .card-header {
  border-bottom: none;
  padding-bottom: 8px;
}

.progress-list {
  padding: 0 20px 16px;
}

.progress-item {
  padding: 12px 0;
  border-bottom: 1px dashed #f1f5f9;
}

.progress-item:last-child {
  border-bottom: none;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-name {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.progress-count {
  font-size: 12px;
  color: #64748b;
}

/* 响应式 */
@media (max-width: 1600px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1400px) {
  .charts-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .trend-chart {
    grid-column: span 2;
  }

  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .trend-chart {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 20px 16px;
    border-radius: 0 0 16px 16px;
  }

  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .header-right {
    width: 100%;
    flex-wrap: wrap;
  }

  .stats-grid,
  .charts-grid,
  .bottom-grid {
    padding: 0 16px;
  }

  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-value {
    font-size: 24px;
  }
}
</style>
