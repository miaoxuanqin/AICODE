const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "海南省住建厅行业知识图谱解决方案";
pres.author = "AI Solutions";

// Color palette - Ocean Gradient (政府/政务风格)
const COLORS = {
  primary: "065A82",
  secondary: "1C7293",
  accent: "FFFFFF",
  dark: "0A3D62",
  light: "F0F7FA",
  text: "1E293B",
  muted: "64748B",
  gold: "D4A84B"
};

const makeShadow = () => ({ type: "outer", blur: 4, offset: 2, angle: 135, color: "000000", opacity: 0.12 });

// ============ SLIDE 1: 封面 ============
let slide1 = pres.addSlide();
slide1.background = { color: COLORS.primary };

slide1.addShape(pres.shapes.RECTANGLE, {
  x: 6.5, y: 0, w: 3.5, h: 2.8,
  fill: { color: COLORS.dark, transparency: 35 }
});

slide1.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 4.2, w: 5, h: 1.425,
  fill: { color: COLORS.dark, transparency: 25 }
});

slide1.addShape(pres.shapes.RECTANGLE, {
  x: 3.5, y: 1.6, w: 3, h: 0.04,
  fill: { color: COLORS.gold }
});

slide1.addText("海南省住建厅", {
  x: 0.5, y: 1.8, w: 9, h: 0.7,
  fontSize: 28, fontFace: "Arial", color: COLORS.secondary, align: "center"
});

slide1.addText("行业知识图谱解决方案", {
  x: 0.5, y: 2.5, w: 9, h: 1.0,
  fontSize: 42, fontFace: "Arial Black", color: COLORS.accent, bold: true, align: "center"
});

slide1.addText("智慧住建 · 知识赋能", {
  x: 0.5, y: 3.6, w: 9, h: 0.5,
  fontSize: 20, fontFace: "Arial", color: COLORS.gold, align: "center"
});

slide1.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 5.1, w: 10, h: 0.525,
  fill: { color: COLORS.dark }
});

slide1.addText("2026 年 5 月", {
  x: 0.5, y: 5.2, w: 9, h: 0.4,
  fontSize: 14, fontFace: "Arial", color: COLORS.secondary, align: "center"
});

// ============ SLIDE 2: 目录 ============
let slide2 = pres.addSlide();
slide2.background = { color: COLORS.light };

slide2.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: COLORS.primary }
});

slide2.addText("目录", {
  x: 0.5, y: 0.4, w: 9, h: 0.8,
  fontSize: 36, fontFace: "Arial Black", color: COLORS.primary, bold: true
});

const tocItems = [
  { num: "01", title: "客户及行业背景" },
  { num: "02", title: "业务痛点分析" },
  { num: "03", title: "AI 解决方案思路" },
  { num: "04", title: "系统技术架构" },
  { num: "05", title: "Demo 演示说明" },
  { num: "06", title: "后续可推进项目机会" }
];

tocItems.forEach((item, i) => {
  const y = 1.4 + i * 0.65;
  slide2.addShape(pres.shapes.OVAL, {
    x: 0.8, y: y, w: 0.45, h: 0.45,
    fill: { color: COLORS.primary }
  });

  slide2.addText(item.num, {
    x: 0.8, y: y, w: 0.45, h: 0.45,
    fontSize: 12, fontFace: "Arial", color: COLORS.accent, bold: true, align: "center", valign: "middle"
  });

  slide2.addText(item.title, {
    x: 1.45, y: y, w: 7, h: 0.45,
    fontSize: 18, fontFace: "Arial", color: COLORS.text, valign: "middle"
  });
});

// ============ SLIDE 3: 客户及行业背景 ============
let slide3 = pres.addSlide();
slide3.background = { color: COLORS.light };

slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: COLORS.primary }
});

slide3.addText("01  客户及行业背景", {
  x: 0.5, y: 0.2, w: 9, h: 0.6,
  fontSize: 24, fontFace: "Arial Black", color: COLORS.accent, bold: true
});

// Client info card
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.1, w: 4.3, h: 1.8,
  fill: { color: COLORS.accent },
  shadow: makeShadow()
});

slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.1, w: 0.08, h: 1.8,
  fill: { color: COLORS.gold }
});

slide3.addText("客户单位", {
  x: 0.8, y: 1.2, w: 3.8, h: 0.35,
  fontSize: 12, fontFace: "Arial", color: COLORS.muted
});

slide3.addText("海南省城乡住房建设厅", {
  x: 0.8, y: 1.55, w: 3.8, h: 0.45,
  fontSize: 18, fontFace: "Arial", color: COLORS.primary, bold: true
});

slide3.addText("省级住建和综合执法领域知识体系建设和服务中心", {
  x: 0.8, y: 2.05, w: 3.8, h: 0.7,
  fontSize: 11, fontFace: "Arial", color: COLORS.text
});

// Business scope card
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 5.2, y: 1.1, w: 4.3, h: 1.8,
  fill: { color: COLORS.accent },
  shadow: makeShadow()
});

slide3.addShape(pres.shapes.RECTANGLE, {
  x: 5.2, y: 1.1, w: 0.08, h: 1.8,
  fill: { color: COLORS.secondary }
});

slide3.addText("业务范围", {
  x: 5.5, y: 1.2, w: 3.8, h: 0.35,
  fontSize: 12, fontFace: "Arial", color: COLORS.muted
});

slide3.addText("全省住建领域统一管理", {
  x: 5.5, y: 1.55, w: 3.8, h: 0.45,
  fontSize: 16, fontFace: "Arial", color: COLORS.primary, bold: true
});

slide3.addText("市场管理 · 综合执法 · 工程质量监督 · 安全监督", {
  x: 5.5, y: 2.05, w: 3.8, h: 0.7,
  fontSize: 10, fontFace: "Arial", color: COLORS.text
});

// Knowledge areas
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 3.1, w: 9, h: 2.2,
  fill: { color: COLORS.accent },
  shadow: makeShadow()
});

slide3.addText("知识图谱覆盖范围", {
  x: 0.8, y: 3.25, w: 8.4, h: 0.4,
  fontSize: 16, fontFace: "Arial", color: COLORS.primary, bold: true
});

const knowledgeAreas = [
  { icon: "市场", desc: "企业资质\n市场准入" },
  { icon: "工商", desc: "营业执照\n经营状态" },
  { icon: "城管", desc: "城市管理\n执法" },
  { icon: "违建", desc: "违法建筑\n查处" },
  { icon: "工地", desc: "工程施工\n监管" },
  { icon: "环保", desc: "环境保护\n要求" },
  { icon: "园林", desc: "园林绿化\n管理" }
];

knowledgeAreas.forEach((area, i) => {
  const x = 0.7 + i * 1.25;

  slide3.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 3.75, w: 1.15, h: 1.35,
    fill: { color: COLORS.light },
    line: { color: COLORS.secondary, width: 1 }
  });

  slide3.addText(area.icon, {
    x: x, y: 3.8, w: 1.15, h: 0.45,
    fontSize: 14, fontFace: "Arial", color: COLORS.primary, bold: true, align: "center"
  });

  slide3.addText(area.desc, {
    x: x, y: 4.25, w: 1.15, h: 0.75,
    fontSize: 9, fontFace: "Arial", color: COLORS.muted, align: "center"
  });
});

// ============ SLIDE 4: 业务痛点 ============
let slide4 = pres.addSlide();
slide4.background = { color: COLORS.light };

slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: COLORS.primary }
});

slide4.addText("02  业务痛点分析", {
  x: 0.5, y: 0.2, w: 9, h: 0.6,
  fontSize: 24, fontFace: "Arial Black", color: COLORS.accent, bold: true
});

const painPoints = [
  {
    title: "知识分散难整合",
    desc: "政策法规、技术标准、执法案例分散于各部门，无法统一检索利用",
    impact: "检索效率低"
  },
  {
    title: "业务人员依赖经验",
    desc: "专家经验难以沉淀传承，新员工上手周期长，人才断层风险高",
    impact: "培训成本高"
  },
  {
    title: "执法依据查找繁琐",
    desc: "综合执法涉及多行业多法规，查找匹配耗时，准确率不稳定",
    impact: "执法效率低"
  },
  {
    title: "知识更新不同步",
    desc: "新政策新规范出台后，各系统知识库无法及时同步更新",
    impact: "信息滞后"
  }
];

painPoints.forEach((point, i) => {
  const col = i % 2;
  const row = Math.floor(i / 2);
  const x = 0.5 + col * 4.6;
  const y = 1.1 + row * 2.1;

  slide4.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: 4.3, h: 1.9,
    fill: { color: COLORS.accent },
    shadow: makeShadow()
  });

  slide4.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: 4.3, h: 0.08,
    fill: { color: "E74C3C" }
  });

  slide4.addText(point.title, {
    x: x + 0.25, y: y + 0.25, w: 3.8, h: 0.45,
    fontSize: 16, fontFace: "Arial", color: COLORS.primary, bold: true
  });

  slide4.addText(point.desc, {
    x: x + 0.25, y: y + 0.75, w: 3.8, h: 0.7,
    fontSize: 12, fontFace: "Arial", color: COLORS.text
  });

  slide4.addShape(pres.shapes.RECTANGLE, {
    x: x + 0.25, y: y + 1.5, w: 1.3, h: 0.3,
    fill: { color: COLORS.light }
  });

  slide4.addText(point.impact, {
    x: x + 0.25, y: y + 1.5, w: 1.3, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: COLORS.muted, align: "center", valign: "middle"
  });
});

// ============ SLIDE 5: AI 解决方案思路 ============
let slide5 = pres.addSlide();
slide5.background = { color: COLORS.light };

slide5.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: COLORS.primary }
});

slide5.addText("03  AI 解决方案思路", {
  x: 0.5, y: 0.2, w: 9, h: 0.6,
  fontSize: 24, fontFace: "Arial Black", color: COLORS.accent, bold: true
});

const solutions = [
  {
    step: "01",
    title: "住建知识库",
    items: ["综合执法法理知识库", "工程质量安全知识库", "业务规则库", "历史案例库"]
  },
  {
    step: "02",
    title: "知识图谱",
    items: ["多源异构数据抽取", "实体关联构建", "语义理解引擎"]
  },
  {
    step: "03",
    title: "知识搜索门户",
    items: ["一站式聚合搜索", "多视角个性化配置", "智能推荐反馈"]
  },
  {
    step: "04",
    title: "智能应用",
    items: ["执法智能助手", "工程监管助手", "问答机器人"]
  }
];

solutions.forEach((sol, i) => {
  const x = 0.4 + i * 2.35;

  slide5.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.1, w: 2.2, h: 4.2,
    fill: { color: COLORS.accent },
    shadow: makeShadow()
  });

  slide5.addShape(pres.shapes.OVAL, {
    x: x + 0.75, y: 1.3, w: 0.7, h: 0.7,
    fill: { color: COLORS.primary }
  });

  slide5.addText(sol.step, {
    x: x + 0.75, y: 1.3, w: 0.7, h: 0.7,
    fontSize: 18, fontFace: "Arial", color: COLORS.accent, bold: true, align: "center", valign: "middle"
  });

  slide5.addText(sol.title, {
    x: x + 0.1, y: 2.15, w: 2.0, h: 0.45,
    fontSize: 13, fontFace: "Arial", color: COLORS.primary, bold: true, align: "center"
  });

  const itemsText = sol.items.map((item, idx) => ({
    text: item,
    options: { bullet: true, fontSize: 10, color: COLORS.text, breakLine: idx < sol.items.length - 1 }
  }));

  slide5.addText(itemsText, {
    x: x + 0.15, y: 2.7, w: 1.9, h: 2.4
  });

  if (i < 3) {
    slide5.addText("→", {
      x: x + 2.2, y: 2.8, w: 0.25, h: 0.4,
      fontSize: 18, fontFace: "Arial", color: COLORS.secondary, align: "center", valign: "middle"
    });
  }
});

// ============ SLIDE 6: 系统技术架构 ============
let slide6 = pres.addSlide();
slide6.background = { color: COLORS.light };

slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: COLORS.primary }
});

slide6.addText("04  系统技术架构", {
  x: 0.5, y: 0.2, w: 9, h: 0.6,
  fontSize: 24, fontFace: "Arial Black", color: COLORS.accent, bold: true
});

// Architecture layers - top to bottom
// Layer 1: 前端
slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.1, w: 9, h: 0.65,
  fill: { color: COLORS.secondary }
});

slide6.addText("前端层 (Vue3 + Element Plus)", {
  x: 0.7, y: 1.2, w: 3, h: 0.45,
  fontSize: 12, fontFace: "Arial", color: COLORS.accent, bold: true, valign: "middle"
});

slide6.addText("知识搜索门户  |  知识管理  |  执法助手  |  问答助手", {
  x: 4, y: 1.2, w: 5.3, h: 0.45,
  fontSize: 11, fontFace: "Arial", color: COLORS.accent, valign: "middle"
});

// Layer 2: API层
slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.9, w: 9, h: 0.65,
  fill: { color: COLORS.primary }
});

slide6.addText("API层 (FastAPI)", {
  x: 0.7, y: 2.0, w: 2, h: 0.45,
  fontSize: 12, fontFace: "Arial", color: COLORS.accent, bold: true, valign: "middle"
});

slide6.addText("KnowledgeAPI  |  QA API  |  Auth API  |  SearchService  |  QAService  |  ParserService", {
  x: 2.8, y: 2.0, w: 6.5, h: 0.45,
  fontSize: 10, fontFace: "Arial", color: COLORS.accent, valign: "middle"
});

// Layer 3: 数据层
slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 2.7, w: 9, h: 0.65,
  fill: { color: COLORS.dark }
});

slide6.addText("数据层", {
  x: 0.7, y: 2.8, w: 1.5, h: 0.45,
  fontSize: 12, fontFace: "Arial", color: COLORS.accent, bold: true, valign: "middle"
});

slide6.addText("MySQL (元数据)  |  Elasticsearch (全文检索)  |  Qdrant (向量搜索)  |  MiniIO (文件存储)", {
  x: 2.3, y: 2.8, w: 7, h: 0.45,
  fontSize: 10, fontFace: "Arial", color: COLORS.accent, valign: "middle"
});

// Layer 4: AI能力层
slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 3.5, w: 9, h: 0.65,
  fill: { color: "2C5F2D" }
});

slide6.addText("AI能力层", {
  x: 0.7, y: 3.6, w: 1.5, h: 0.45,
  fontSize: 12, fontFace: "Arial", color: COLORS.accent, bold: true, valign: "middle"
});

slide6.addText("Embedding (text2vec-base-chinese)  |  LLM (MiniMax M2.7)  |  RAG 图谱增强问答", {
  x: 2.3, y: 3.6, w: 7, h: 0.45,
  fontSize: 10, fontFace: "Arial", color: COLORS.accent, valign: "middle"
});

// Architecture diagram - right side explanation
slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 4.3, w: 9, h: 1.0,
  fill: { color: COLORS.accent },
  shadow: makeShadow()
});

slide6.addText("技术特点：", {
  x: 0.7, y: 4.4, w: 1.5, h: 0.35,
  fontSize: 12, fontFace: "Arial", color: COLORS.primary, bold: true
});

const techFeatures = [
  { name: "RAG", desc: "检索增强生成" },
  { name: "向量搜索", desc: "语义理解" },
  { name: "知识图谱", desc: "实体关联" },
  { name: "多视角", desc: "个性化配置" }
];

techFeatures.forEach((feat, i) => {
  const x = 0.7 + i * 2.2;
  slide6.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 4.8, w: 0.9, h: 0.4,
    fill: { color: COLORS.secondary }
  });
  slide6.addText(feat.name, {
    x: x, y: 4.8, w: 0.9, h: 0.4,
    fontSize: 11, fontFace: "Arial", color: COLORS.accent, bold: true, align: "center", valign: "middle"
  });
  slide6.addText(feat.desc, {
    x: x + 0.95, y: 4.8, w: 1.1, h: 0.4,
    fontSize: 10, fontFace: "Arial", color: COLORS.muted, valign: "middle"
  });
});

// ============ SLIDE 7: 业务与技术对应 ============
let slide7 = pres.addSlide();
slide7.background = { color: COLORS.light };

slide7.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: COLORS.primary }
});

slide7.addText("04  系统技术架构（续）业务与技术结合", {
  x: 0.5, y: 0.2, w: 9, h: 0.6,
  fontSize: 22, fontFace: "Arial Black", color: COLORS.accent, bold: true
});

// Business-Tech mapping table
const mappingData = [
  { biz: "知识搜索门户", tech: "ES 全文检索 + 多视角配置", desc: "一站式聚合搜索，支持多角色权限" },
  { biz: "执法智能助手", tech: "ES 关键词搜索 + RAG", desc: "依据法律法规推荐执法处置方案" },
  { biz: "工程监管助手", tech: "向量语义搜索 + RAG", desc: "定位匹配监管依据与处置规范" },
  { biz: "问答机器人", tech: "向量搜索 + 多轮对话", desc: "智能问答，支持上下文理解" },
  { biz: "知识库构建", tech: "文本解析 + Embedding + 图谱", desc: "多源异构数据抽取与关联" }
];

mappingData.forEach((item, i) => {
  const y = 1.15 + i * 0.85;

  slide7.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: y, w: 9, h: 0.75,
    fill: { color: COLORS.accent },
    shadow: makeShadow()
  });

  // Business column
  slide7.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: y, w: 1.8, h: 0.75,
    fill: { color: COLORS.secondary }
  });

  slide7.addText(item.biz, {
    x: 0.5, y: y, w: 1.8, h: 0.75,
    fontSize: 12, fontFace: "Arial", color: COLORS.accent, bold: true, align: "center", valign: "middle"
  });

  // Tech column
  slide7.addText(item.tech, {
    x: 2.5, y: y + 0.1, w: 3.2, h: 0.55,
    fontSize: 11, fontFace: "Arial", color: COLORS.primary, bold: true, valign: "middle"
  });

  // Desc column
  slide7.addText(item.desc, {
    x: 5.8, y: y + 0.1, w: 3.5, h: 0.55,
    fontSize: 10, fontFace: "Arial", color: COLORS.muted, valign: "middle"
  });
});

// Key modules section
slide7.addText("核心模块说明", {
  x: 0.5, y: 5.45, w: 2, h: 0.3,
  fontSize: 12, fontFace: "Arial", color: COLORS.primary, bold: true
});

slide7.addText("问答助手 (qa) · 执法助手 (law_general) · 工程监管助手 (supervise) — 差异化 Category 配置与搜索策略", {
  x: 2.5, y: 5.45, w: 7, h: 0.3,
  fontSize: 9, fontFace: "Arial", color: COLORS.muted
});

// ============ SLIDE 8: Demo 演示说明 ============
let slide8 = pres.addSlide();
slide8.background = { color: COLORS.light };

slide8.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: COLORS.primary }
});

slide8.addText("05  Demo 演示说明", {
  x: 0.5, y: 0.2, w: 9, h: 0.6,
  fontSize: 24, fontFace: "Arial Black", color: COLORS.accent, bold: true
});

// Demo intro
slide8.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.05, w: 9, h: 1.1,
  fill: { color: COLORS.accent },
  shadow: makeShadow()
});

slide8.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.05, w: 0.08, h: 1.1,
  fill: { color: "27AE60" }
});

slide8.addText("海南省住建知识库系统", {
  x: 0.85, y: 1.15, w: 8.3, h: 0.4,
  fontSize: 16, fontFace: "Arial", color: COLORS.primary, bold: true
});

slide8.addText("面向全省住建和综合执法领域，提供行业知识应用与住建知识库服务", {
  x: 0.85, y: 1.55, w: 8.3, h: 0.4,
  fontSize: 12, fontFace: "Arial", color: COLORS.text
});

// Demo features
const demoFeatures = [
  {
    title: "知识搜索门户",
    items: ["一站式聚合搜索", "多视角个性化配置", "热点/最新知识展示", "知识评论收藏点赞"]
  },
  {
    title: "智能助手",
    items: ["执法智能助手", "工程监管智能助手", "多轮对话引导", "智能推荐"]
  },
  {
    title: "问答助手",
    items: ["一问一答", "多轮问答", "输入联想", "服务评价统计"]
  }
];

demoFeatures.forEach((feat, i) => {
  const x = 0.5 + i * 3.05;

  slide8.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 2.35, w: 2.9, h: 2.95,
    fill: { color: COLORS.accent },
    shadow: makeShadow()
  });

  slide8.addShape(pres.shapes.OVAL, {
    x: x + 1.05, y: 2.5, w: 0.8, h: 0.8,
    fill: { color: COLORS.secondary }
  });

  slide8.addText(String(i + 1).padStart(2, "0"), {
    x: x + 1.05, y: 2.5, w: 0.8, h: 0.8,
    fontSize: 18, fontFace: "Arial", color: COLORS.accent, bold: true, align: "center", valign: "middle"
  });

  slide8.addText(feat.title, {
    x: x + 0.15, y: 3.4, w: 2.6, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: COLORS.primary, bold: true, align: "center"
  });

  const itemsText = feat.items.map((item, idx) => ({
    text: item,
    options: { bullet: true, fontSize: 10, color: COLORS.text, breakLine: idx < feat.items.length - 1 }
  }));

  slide8.addText(itemsText, {
    x: x + 0.25, y: 3.85, w: 2.4, h: 1.3
  });
});

// ============ SLIDE 9: 后续可推进项目机会 ============
let slide9 = pres.addSlide();
slide9.background = { color: COLORS.light };

slide9.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: COLORS.primary }
});

slide9.addText("06  后续可推进项目机会", {
  x: 0.5, y: 0.2, w: 9, h: 0.6,
  fontSize: 24, fontFace: "Arial Black", color: COLORS.accent, bold: true
});

const projects = [
  {
    phase: "第一阶段",
    title: "省级住建知识库建设",
    desc: "构建综合执法法理知识库、工程质量安全知识库、业务规则库、历史案例库",
    priority: "高"
  },
  {
    phase: "第二阶段",
    title: "知识图谱与智能引擎",
    desc: "建设住建知识引擎，实现多源异构数据抽取、实体关联构建、语义理解",
    priority: "高"
  },
  {
    phase: "第三阶段",
    title: "智能应用全面落地",
    desc: "执法智能助手、工程监管助手、问答机器人等智能应用上线",
    priority: "中"
  },
  {
    phase: "远期规划",
    title: "全省知识体系统一",
    desc: "推动各地市知识门户建设，实现全省住建知识一体化服务",
    priority: "中"
  }
];

projects.forEach((proj, i) => {
  const y = 1.05 + i * 1.1;

  slide9.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: y, w: 9, h: 0.95,
    fill: { color: COLORS.accent },
    shadow: makeShadow()
  });

  slide9.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: y + 0.25, w: 1.2, h: 0.45,
    fill: { color: COLORS.primary }
  });

  slide9.addText(proj.phase, {
    x: 0.7, y: y + 0.25, w: 1.2, h: 0.45,
    fontSize: 11, fontFace: "Arial", color: COLORS.accent, bold: true, align: "center", valign: "middle"
  });

  slide9.addText(proj.title, {
    x: 2.1, y: y + 0.15, w: 4.5, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: COLORS.primary, bold: true
  });

  slide9.addText(proj.desc, {
    x: 2.1, y: y + 0.52, w: 5.5, h: 0.35,
    fontSize: 10, fontFace: "Arial", color: COLORS.muted
  });

  const badgeColor = proj.priority === "高" ? "E74C3C" : "F39C12";
  slide9.addShape(pres.shapes.RECTANGLE, {
    x: 8.5, y: y + 0.3, w: 0.7, h: 0.35,
    fill: { color: badgeColor }
  });

  slide9.addText(proj.priority, {
    x: 8.5, y: y + 0.3, w: 0.7, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: COLORS.accent, bold: true, align: "center", valign: "middle"
  });
});

// ============ SLIDE 10: 感谢页 ============
let slide10 = pres.addSlide();
slide10.background = { color: COLORS.primary };

slide10.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 3.5, h: 5.625,
  fill: { color: COLORS.dark, transparency: 30 }
});

slide10.addShape(pres.shapes.RECTANGLE, {
  x: 6.5, y: 2.2, w: 3.5, h: 3.425,
  fill: { color: COLORS.dark, transparency: 25 }
});

slide10.addShape(pres.shapes.RECTANGLE, {
  x: 3.5, y: 2.0, w: 3, h: 0.04,
  fill: { color: COLORS.gold }
});

slide10.addText("感谢聆听", {
  x: 0.5, y: 2.2, w: 9, h: 0.9,
  fontSize: 44, fontFace: "Arial Black", color: COLORS.accent, bold: true, align: "center"
});

slide10.addText("期待与海南省住建厅深入合作", {
  x: 0.5, y: 3.2, w: 9, h: 0.6,
  fontSize: 20, fontFace: "Arial", color: COLORS.secondary, align: "center"
});

slide10.addText("智慧住建 · 知识赋能", {
  x: 0.5, y: 4.0, w: 9, h: 0.5,
  fontSize: 16, fontFace: "Arial", color: COLORS.gold, align: "center"
});

// Save
pres.writeFile({ fileName: "C:\\AICODE3\\ppt_output\\海南省住建厅行业知识图谱解决方案_v2.pptx" })
  .then(() => console.log("PPT created successfully!"))
  .catch(err => console.error("Error:", err));