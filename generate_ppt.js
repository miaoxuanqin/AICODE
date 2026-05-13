const pptxgen = require("pptxgenjs");

// 创建演示文稿
let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "海南省住建行业知识图谱AI解决方案";
pres.author = "东方金信";
pres.company = "北京东方金信科技股份有限公司";

// 配色方案 - Ocean Gradient 风格（政务蓝色系）
const COLORS = {
  primary: "1A365D",
  secondary: "2B6CB0",
  accent: "4299E1",
  light: "EBF8FF",
  white: "FFFFFF",
  dark: "1A202C",
  gray: "718096",
  lightGray: "E2E8F0",
  success: "38A169",
  warning: "DD6B20",
};

// 阴影工厂函数
const makeShadow = () => ({
  type: "outer",
  color: "000000",
  blur: 8,
  offset: 3,
  angle: 135,
  opacity: 0.12
});

const makeCardShadow = () => ({
  type: "outer",
  color: "000000",
  blur: 6,
  offset: 2,
  angle: 135,
  opacity: 0.10
});

// ============================================================
// 第1页：封面
// ============================================================
let slide1 = pres.addSlide();
slide1.background = { color: COLORS.primary };

// 装饰性圆形
slide1.addShape(pres.shapes.OVAL, {
  x: -1.5, y: -1.5, w: 4, h: 4,
  fill: { color: COLORS.secondary, transparency: 60 }
});
slide1.addShape(pres.shapes.OVAL, {
  x: 7.5, y: 3.5, w: 4, h: 4,
  fill: { color: COLORS.accent, transparency: 70 }
});

// 顶部装饰线
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 0.8, w: 0.8, h: 0.06,
  fill: { color: COLORS.accent }
});

// 主标题
slide1.addText("海南省住建行业", {
  x: 0.5, y: 1.6, w: 9, h: 0.9,
  fontSize: 44, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, align: "left"
});
slide1.addText("知识图谱AI解决方案", {
  x: 0.5, y: 2.4, w: 9, h: 0.9,
  fontSize: 44, fontFace: "Microsoft YaHei",
  color: COLORS.accent, bold: true, align: "left"
});

// 副标题
slide1.addText("智能知识引擎驱动住建与综合执法数字化转型", {
  x: 0.5, y: 3.6, w: 9, h: 0.5,
  fontSize: 20, fontFace: "Microsoft YaHei",
  color: COLORS.white, align: "left"
});

// 分隔线
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 4.3, w: 3, h: 0.02,
  fill: { color: COLORS.accent }
});

// 公司信息
slide1.addText("北京东方金信科技股份有限公司", {
  x: 0.5, y: 4.6, w: 5, h: 0.4,
  fontSize: 16, fontFace: "Microsoft YaHei",
  color: COLORS.white, align: "left"
});
slide1.addText("2026年5月", {
  x: 0.5, y: 5.0, w: 5, h: 0.4,
  fontSize: 14, fontFace: "Microsoft YaHei",
  color: COLORS.lightGray, align: "left"
});

// ============================================================
// 第2页：客户及行业背景
// ============================================================
let slide2 = pres.addSlide();
slide2.background = { color: COLORS.white };

slide2.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 1.0,
  fill: { color: COLORS.primary }
});
slide2.addText("客户及行业背景", {
  x: 0.5, y: 0.25, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});

// 客户概况卡片
slide2.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.3, w: 4.3, h: 1.8,
  fill: { color: COLORS.light },
  shadow: makeCardShadow()
});
slide2.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.3, w: 0.08, h: 1.8,
  fill: { color: COLORS.secondary }
});
slide2.addText("客户概况", {
  x: 0.75, y: 1.45, w: 4, h: 0.4,
  fontSize: 16, fontFace: "Microsoft YaHei",
  color: COLORS.primary, bold: true, margin: 0
});
slide2.addText([
  { text: "海南省住房和城乡建设厅", options: { bold: true, breakLine: true } },
  { text: "承担全省住建领域的行政管理职责", options: { breakLine: true } }
], {
  x: 0.75, y: 1.85, w: 3.9, h: 1.1,
  fontSize: 13, fontFace: "Microsoft YaHei",
  color: COLORS.dark, margin: 0
});

// 业务范围卡片
slide2.addShape(pres.shapes.RECTANGLE, {
  x: 5.2, y: 1.3, w: 4.3, h: 1.8,
  fill: { color: COLORS.light },
  shadow: makeCardShadow()
});
slide2.addShape(pres.shapes.RECTANGLE, {
  x: 5.2, y: 1.3, w: 0.08, h: 1.8,
  fill: { color: COLORS.accent }
});
slide2.addText("业务范围", {
  x: 5.45, y: 1.45, w: 4, h: 0.4,
  fontSize: 16, fontFace: "Microsoft YaHei",
  color: COLORS.primary, bold: true, margin: 0
});
slide2.addText([
  { text: "- 工程建设监管", options: { breakLine: true } },
  { text: "- 综合行政执法", options: { breakLine: true } },
  { text: "- 城市管理", options: {} }
], {
  x: 5.45, y: 1.85, w: 3.9, h: 1.1,
  fontSize: 13, fontFace: "Microsoft YaHei",
  color: COLORS.dark, margin: 0
});

// 行业背景标题
slide2.addText("行业背景趋势", {
  x: 0.5, y: 3.3, w: 9, h: 0.4,
  fontSize: 18, fontFace: "Microsoft YaHei",
  color: COLORS.primary, bold: true, margin: 0
});

// 三个趋势卡片
const trends = [
  { title: "业务量快速增长", desc: "建设项目持续增加\n执法事项已扩展至200+项", color: COLORS.secondary },
  { title: "知识体系庞杂", desc: "涉及法律法规上百部\n技术标准规范数量庞大", color: COLORS.accent },
  { title: "信息化初步建立", desc: "已有质监、安监、城管系统\n数据分散难以共享", color: COLORS.success }
];

trends.forEach((item, i) => {
  const x = 0.5 + i * 3.1;
  slide2.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 3.8, w: 2.9, h: 1.6,
    fill: { color: COLORS.white },
    line: { color: item.color, width: 2 },
    shadow: makeCardShadow()
  });
  slide2.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 3.8, w: 2.9, h: 0.08,
    fill: { color: item.color }
  });
  slide2.addText(item.title, {
    x: x + 0.15, y: 3.95, w: 2.6, h: 0.4,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: COLORS.primary, bold: true, margin: 0
  });
  slide2.addText(item.desc, {
    x: x + 0.15, y: 4.35, w: 2.6, h: 0.95,
    fontSize: 11, fontFace: "Microsoft YaHei",
    color: COLORS.gray, margin: 0
  });
});

// ============================================================
// 第3页：业务痛点
// ============================================================
let slide3 = pres.addSlide();
slide3.background = { color: COLORS.white };

slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 1.0,
  fill: { color: COLORS.primary }
});
slide3.addText("业务痛点", {
  x: 0.5, y: 0.25, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});

// 四个痛点卡片 2x2 布局
const pains = [
  { num: "01", title: "知识分散难找", problem: "法规文件、技术规范、执法依据分散在各个系统和文档中", impact: "知识检索耗时30分钟以上，效率低下" },
  { num: "02", title: "执法标准不统一", problem: "综合执法事项多、依据杂，不同人员理解各异", impact: "执法结果存在差异，易引发行政诉讼" },
  { num: "03", title: "业务学习成本高", problem: "住建与综合执法高度专业化，新人熟悉业务周期长", impact: "人才培养周期3-6个月，专家经验难传承" },
  { num: "04", title: "知识复用率低", problem: "历史执法案例、整改经验散落各处", impact: "同类问题重复研究，重复工作" }
];

pains.forEach((item, i) => {
  const row = Math.floor(i / 2);
  const col = i % 2;
  const x = 0.5 + col * 4.7;
  const y = 1.25 + row * 2.1;

  slide3.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: 4.4, h: 1.95,
    fill: { color: COLORS.white },
    line: { color: COLORS.lightGray, width: 1 },
    shadow: makeCardShadow()
  });

  slide3.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: 0.06, h: 1.95,
    fill: { color: COLORS.warning }
  });

  slide3.addText(item.num, {
    x: x + 0.2, y: y + 0.15, w: 0.5, h: 0.4,
    fontSize: 22, fontFace: "Georgia",
    color: COLORS.secondary, bold: true, margin: 0
  });

  slide3.addText(item.title, {
    x: x + 0.7, y: y + 0.15, w: 3.5, h: 0.4,
    fontSize: 16, fontFace: "Microsoft YaHei",
    color: COLORS.primary, bold: true, margin: 0
  });

  slide3.addText(item.problem, {
    x: x + 0.2, y: y + 0.6, w: 4.0, h: 0.6,
    fontSize: 11, fontFace: "Microsoft YaHei",
    color: COLORS.dark, margin: 0
  });

  slide3.addText("> " + item.impact, {
    x: x + 0.2, y: y + 1.25, w: 4.0, h: 0.55,
    fontSize: 11, fontFace: "Microsoft YaHei",
    color: COLORS.warning, margin: 0
  });
});

// ============================================================
// 第4页：AI解决方案思路
// ============================================================
let slide4 = pres.addSlide();
slide4.background = { color: COLORS.white };

slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 1.0,
  fill: { color: COLORS.primary }
});
slide4.addText("AI解决方案思路", {
  x: 0.5, y: 0.25, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});

// 核心理念
slide4.addText("一个引擎 + 两大支撑 + 三类应用", {
  x: 0.5, y: 1.15, w: 9, h: 0.4,
  fontSize: 18, fontFace: "Microsoft YaHei",
  color: COLORS.secondary, bold: true, align: "center", margin: 0
});

// 应用层
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.7, w: 9, h: 1.1,
  fill: { color: COLORS.accent },
  shadow: makeCardShadow()
});
slide4.addText("用户层 - 三类应用", {
  x: 0.7, y: 1.8, w: 2, h: 0.35,
  fontSize: 12, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});

const apps = ["知识搜索门户", "智能助手", "问答助手"];
apps.forEach((app, i) => {
  slide4.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.7 + i * 2.95, y: 2.2, w: 2.7, h: 0.45,
    fill: { color: COLORS.white },
    rectRadius: 0.05
  });
  slide4.addText(app, {
    x: 0.7 + i * 2.95, y: 2.2, w: 2.7, h: 0.45,
    fontSize: 13, fontFace: "Microsoft YaHei",
    color: COLORS.primary, bold: true, align: "center", valign: "middle", margin: 0
  });
});

// 箭头
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 4.7, y: 2.85, w: 0.6, h: 0.25,
  fill: { color: COLORS.secondary }
});

// 引擎层
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 3.15, w: 9, h: 0.9,
  fill: { color: COLORS.secondary },
  shadow: makeCardShadow()
});
slide4.addText("住建知识引擎 - 核心大脑", {
  x: 0.7, y: 3.3, w: 2.5, h: 0.3,
  fontSize: 12, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});
slide4.addText("智能搜索  |  知识推荐  |  智能推理  |  图谱分析", {
  x: 3.2, y: 3.4, w: 6, h: 0.4,
  fontSize: 14, fontFace: "Microsoft YaHei",
  color: COLORS.white, align: "center", margin: 0
});

// 箭头
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 4.7, y: 4.1, w: 0.6, h: 0.25,
  fill: { color: COLORS.gray }
});

// 知识层
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 4.4, w: 9, h: 1.05,
  fill: { color: COLORS.primary },
  shadow: makeCardShadow()
});
slide4.addText("知识层 - 两大支撑", {
  x: 0.7, y: 4.5, w: 1.8, h: 0.3,
  fontSize: 12, fontFace: "Microsoft YaHei",
  color: COLORS.lightGray, bold: true, margin: 0
});

const libs = [
  { name: "法理知识库", desc: "法规/执法事项/裁量基准" },
  { name: "工程安全知识库", desc: "技术标准/检查清单/隐患案例" },
  { name: "业务规则库", desc: "审批流程/监管规程/预警规则" },
  { name: "历史案例库", desc: "执法案例/整改案例/事故案例" }
];

libs.forEach((lib, i) => {
  const libX = 0.65 + i * 2.25;
  slide4.addShape(pres.shapes.RECTANGLE, {
    x: libX, y: 4.85, w: 2.1, h: 0.5,
    fill: { color: COLORS.white },
    transparency: 15
  });
  slide4.addText(lib.name, {
    x: libX, y: 4.85, w: 2.1, h: 0.28,
    fontSize: 11, fontFace: "Microsoft YaHei",
    color: COLORS.white, bold: true, align: "center", valign: "middle", margin: 0
  });
  slide4.addText(lib.desc, {
    x: libX, y: 5.1, w: 2.1, h: 0.25,
    fontSize: 8, fontFace: "Microsoft YaHei",
    color: COLORS.lightGray, align: "center", valign: "middle", margin: 0
  });
});

// ============================================================
// 第5页：技术架构
// ============================================================
let slide5 = pres.addSlide();
slide5.background = { color: COLORS.white };

slide5.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 1.0,
  fill: { color: COLORS.primary }
});
slide5.addText("技术架构", {
  x: 0.5, y: 0.25, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});

// 四层架构
const techLayers = [
  { name: "用户层", color: COLORS.accent, items: ["Web门户", "移动端", "业务系统集成"] },
  { name: "应用层", color: COLORS.secondary, items: ["搜索服务", "推荐服务", "问答服务", "推理服务", "图谱服务"] },
  { name: "知识层", color: COLORS.primary, items: ["法理知识库", "安全知识库", "规则知识库", "案例库"] },
  { name: "数据层", color: "2D3748", items: ["知识抽取NLP", "知识融合", "图数据库", "向量检索"] }
];

techLayers.forEach((layer, i) => {
  const y = 1.2 + i * 1.05;

  slide5.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: y, w: 1.3, h: 0.85,
    fill: { color: layer.color }
  });
  slide5.addText(layer.name, {
    x: 0.5, y: y, w: 1.3, h: 0.85,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: COLORS.white, bold: true, align: "center", valign: "middle", margin: 0
  });

  slide5.addShape(pres.shapes.RECTANGLE, {
    x: 1.9, y: y, w: 7.6, h: 0.85,
    fill: { color: COLORS.light },
    shadow: makeCardShadow()
  });

  const itemW = 7.4 / layer.items.length;
  layer.items.forEach((item, j) => {
    slide5.addText(item, {
      x: 2.0 + j * itemW, y: y, w: itemW, h: 0.85,
      fontSize: 11, fontFace: "Microsoft YaHei",
      color: COLORS.dark, align: "center", valign: "middle", margin: 0
    });
    if (j < layer.items.length - 1) {
      slide5.addShape(pres.shapes.LINE, {
        x: 2.0 + (j + 1) * itemW, y: y + 0.15,
        w: 0, h: 0.55,
        line: { color: COLORS.lightGray, width: 1 }
      });
    }
  });
});

// 核心技术说明
slide5.addText("核心技术能力", {
  x: 0.5, y: 5.35, w: 2, h: 0.25,
  fontSize: 12, fontFace: "Microsoft YaHei",
  color: COLORS.primary, bold: true, margin: 0
});

const techs = ["自然语言理解(NLU)", "语义搜索匹配", "知识图谱构建", "智能问答推理"];
techs.forEach((tech, i) => {
  slide5.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5 + i * 2.35, y: 5.6, w: 2.2, h: 0.0,
    fill: { color: COLORS.secondary },
    rectRadius: 0.03
  });
  slide5.addText(tech, {
    x: 0.5 + i * 2.35, y: 5.55, w: 2.2, h: 0.3,
    fontSize: 10, fontFace: "Microsoft YaHei",
    color: COLORS.white, align: "center", valign: "middle", margin: 0
  });
});

// ============================================================
// 第6页：业务架构
// ============================================================
let slide6 = pres.addSlide();
slide6.background = { color: COLORS.white };

slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 1.0,
  fill: { color: COLORS.primary }
});
slide6.addText("业务架构 - 知识中台", {
  x: 0.5, y: 0.25, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});

// 知识搜索门户层
slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.2, w: 9, h: 0.8,
  fill: { color: COLORS.accent },
  shadow: makeCardShadow()
});
slide6.addText("知识搜索门户", {
  x: 0.7, y: 1.28, w: 2, h: 0.3,
  fontSize: 14, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});
const portalFeatures = ["多视角配置", "热点推荐", "知识分类", "评论收藏", "权限管理"];
portalFeatures.forEach((f, i) => {
  slide6.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.7 + i * 1.75, y: 1.62, w: 1.6, h: 0.3,
    fill: { color: COLORS.white },
    transparency: 20,
    rectRadius: 0.03
  });
  slide6.addText(f, {
    x: 0.7 + i * 1.75, y: 1.62, w: 1.6, h: 0.3,
    fontSize: 10, fontFace: "Microsoft YaHei",
    color: COLORS.white, align: "center", valign: "middle", margin: 0
  });
});

// 智能应用服务层
slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 2.1, w: 9, h: 1.35,
  fill: { color: COLORS.secondary },
  shadow: makeCardShadow()
});
slide6.addText("智能应用服务", {
  x: 0.7, y: 2.18, w: 2, h: 0.3,
  fontSize: 14, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});

const smartApps = [
  { name: "执法智能助手", features: "立案辅助 / 处置推荐 / 文书生成" },
  { name: "工程监管助手", features: "质量监督 / 安全监管 / 问题诊断" },
  { name: "问答助手", features: "一键问答 / 多轮对话 / 知识推荐" }
];

smartApps.forEach((app, i) => {
  const appX = 0.7 + i * 2.95;
  slide6.addShape(pres.shapes.RECTANGLE, {
    x: appX, y: 2.55, w: 2.8, h: 0.8,
    fill: { color: COLORS.white },
    transparency: 15
  });
  slide6.addText(app.name, {
    x: appX, y: 2.58, w: 2.8, h: 0.35,
    fontSize: 12, fontFace: "Microsoft YaHei",
    color: COLORS.white, bold: true, align: "center", margin: 0
  });
  slide6.addText(app.features, {
    x: appX, y: 2.93, w: 2.8, h: 0.35,
    fontSize: 9, fontFace: "Microsoft YaHei",
    color: COLORS.light, align: "center", margin: 0
  });
});

// 住建知识引擎层
slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 3.55, w: 9, h: 0.65,
  fill: { color: COLORS.primary },
  shadow: makeCardShadow()
});
slide6.addText("住建知识引擎  -  搜索  |  推荐  |  推理  |  分析  |  监控", {
  x: 0.7, y: 3.55, w: 8.6, h: 0.65,
  fontSize: 14, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, align: "center", valign: "middle", margin: 0
});

// 住建知识库层
slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 4.3, w: 9, h: 1.15,
  fill: { color: "2D3748" },
  shadow: makeCardShadow()
});
slide6.addText("住建知识库", {
  x: 0.7, y: 4.38, w: 1.5, h: 0.3,
  fontSize: 14, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});

const dbLibs = [
  { name: "法理知识库", items: "法规条文/执法事项/裁量基准" },
  { name: "安全知识库", items: "技术标准/检查清单/隐患案例" },
  { name: "业务规则库", items: "审批流程/监管规程/预警规则" },
  { name: "历史案例库", items: "执法案例/整改案例/事故案例" }
];

dbLibs.forEach((lib, i) => {
  const libX = 0.7 + i * 2.25;
  slide6.addShape(pres.shapes.RECTANGLE, {
    x: libX, y: 4.72, w: 2.1, h: 0.65,
    fill: { color: COLORS.white },
    transparency: 10
  });
  slide6.addText(lib.name, {
    x: libX, y: 4.75, w: 2.1, h: 0.3,
    fontSize: 11, fontFace: "Microsoft YaHei",
    color: COLORS.white, bold: true, align: "center", margin: 0
  });
  slide6.addText(lib.items, {
    x: libX, y: 5.02, w: 2.1, h: 0.3,
    fontSize: 8, fontFace: "Microsoft YaHei",
    color: COLORS.lightGray, align: "center", margin: 0
  });
});

// ============================================================
// 第7页：Demo演示说明
// ============================================================
let slide7 = pres.addSlide();
slide7.background = { color: COLORS.white };

slide7.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 1.0,
  fill: { color: COLORS.primary }
});
slide7.addText("Demo演示说明", {
  x: 0.5, y: 0.25, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});

// 三个Demo场景
const demos = [
  { num: "Demo 1", title: "知识搜索门户", subtitle: "一句话找答案", input: "输入：工地扬尘超标如何处理？", output: "返回：海南省大气污染防治条例、处罚标准、关联案例、防治标准", value: "查找时间：30分钟 > 3分钟" },
  { num: "Demo 2", title: "执法智能助手", subtitle: "智能辅助立案", input: "输入：擅自倾倒建筑垃圾违法行为", output: "返回：适用法规、处罚依据、类似案例、处置方案建议", value: "立案时间：2小时 > 20分钟" },
  { num: "Demo 3", title: "工程监管助手", subtitle: "问题诊断与建议", input: "输入：工地混凝土表面裂缝问题", output: "返回：问题类型、严重程度判定、适用标准、处理建议", value: "问题定位：快速准确，有据可依" }
];

demos.forEach((demo, i) => {
  const y = 1.2 + i * 1.45;

  slide7.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: y, w: 9, h: 1.35,
    fill: { color: COLORS.white },
    line: { color: COLORS.lightGray, width: 1 },
    shadow: makeCardShadow()
  });

  slide7.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: y, w: 0.08, h: 1.35,
    fill: { color: COLORS.accent }
  });

  slide7.addText(demo.num, {
    x: 0.75, y: y + 0.1, w: 1.2, h: 0.3,
    fontSize: 11, fontFace: "Microsoft YaHei",
    color: COLORS.secondary, bold: true, margin: 0
  });
  slide7.addText(demo.title, {
    x: 1.9, y: y + 0.08, w: 2, h: 0.35,
    fontSize: 15, fontFace: "Microsoft YaHei",
    color: COLORS.primary, bold: true, margin: 0
  });
  slide7.addText(demo.subtitle, {
    x: 3.9, y: y + 0.12, w: 1.5, h: 0.28,
    fontSize: 10, fontFace: "Microsoft YaHei",
    color: COLORS.accent, margin: 0
  });

  slide7.addText(demo.input, {
    x: 0.75, y: y + 0.48, w: 4, h: 0.25,
    fontSize: 10, fontFace: "Microsoft YaHei",
    color: COLORS.gray, margin: 0
  });

  slide7.addText(demo.output, {
    x: 0.75, y: y + 0.75, w: 5.5, h: 0.25,
    fontSize: 10, fontFace: "Microsoft YaHei",
    color: COLORS.dark, margin: 0
  });

  slide7.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 6.8, y: y + 0.45, w: 2.5, h: 0.7,
    fill: { color: COLORS.success },
    rectRadius: 0.05
  });
  slide7.addText(demo.value, {
    x: 6.8, y: y + 0.45, w: 2.5, h: 0.7,
    fontSize: 11, fontFace: "Microsoft YaHei",
    color: COLORS.white, bold: true, align: "center", valign: "middle", margin: 0
  });
});

// ============================================================
// 第8页：业务价值
// ============================================================
let slide8 = pres.addSlide();
slide8.background = { color: COLORS.white };

slide8.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 1.0,
  fill: { color: COLORS.primary }
});
slide8.addText("业务价值", {
  x: 0.5, y: 0.25, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});

// 四个价值指标
const values = [
  { metric: "知识检索", before: "30分钟", after: "3分钟", improvement: "效率提升10倍" },
  { metric: "执法依据匹配率", before: "60%", after: "95%+", improvement: "规范执法" },
  { metric: "新人上手周期", before: "3个月", after: "1个月", improvement: "加速培养" },
  { metric: "历史案例复用", before: "低", after: "3倍以上", improvement: "知识沉淀" }
];

values.forEach((v, i) => {
  const x = 0.5 + i * 2.35;

  slide8.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.25, w: 2.2, h: 2.2,
    fill: { color: COLORS.white },
    line: { color: COLORS.lightGray, width: 1 },
    shadow: makeCardShadow()
  });

  slide8.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.25, w: 2.2, h: 0.06,
    fill: { color: COLORS.accent }
  });

  slide8.addText(v.metric, {
    x: x, y: 1.4, w: 2.2, h: 0.4,
    fontSize: 13, fontFace: "Microsoft YaHei",
    color: COLORS.primary, bold: true, align: "center", margin: 0
  });

  slide8.addText("现状", {
    x: x, y: 1.85, w: 2.2, h: 0.25,
    fontSize: 9, fontFace: "Microsoft YaHei",
    color: COLORS.gray, align: "center", margin: 0
  });
  slide8.addText(v.before, {
    x: x, y: 2.05, w: 2.2, h: 0.35,
    fontSize: 18, fontFace: "Georgia",
    color: COLORS.warning, bold: true, align: "center", margin: 0
  });

  slide8.addText("v", {
    x: x, y: 2.4, w: 2.2, h: 0.3,
    fontSize: 16, fontFace: "Arial",
    color: COLORS.success, bold: true, align: "center", margin: 0
  });

  slide8.addText("目标", {
    x: x, y: 2.65, w: 2.2, h: 0.25,
    fontSize: 9, fontFace: "Microsoft YaHei",
    color: COLORS.gray, align: "center", margin: 0
  });
  slide8.addText(v.after, {
    x: x, y: 2.85, w: 2.2, h: 0.35,
    fontSize: 18, fontFace: "Georgia",
    color: COLORS.success, bold: true, align: "center", margin: 0
  });
});

// 核心价值总结
slide8.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 3.7, w: 9, h: 1.7,
  fill: { color: COLORS.light },
  shadow: makeCardShadow()
});

slide8.addText("核心价值", {
  x: 0.7, y: 3.85, w: 2, h: 0.35,
  fontSize: 16, fontFace: "Microsoft YaHei",
  color: COLORS.primary, bold: true, margin: 0
});

const coreValues = [
  { icon: "01", text: "统一知识门户，打破信息孤岛" },
  { icon: "02", text: "智能辅助决策，降低执法风险" },
  { icon: "03", text: "知识沉淀积累，赋能业务创新" }
];

coreValues.forEach((cv, i) => {
  const cvX = 0.7 + i * 3;
  slide8.addShape(pres.shapes.OVAL, {
    x: cvX, y: 4.3, w: 0.5, h: 0.5,
    fill: { color: COLORS.secondary }
  });
  slide8.addText(cv.icon, {
    x: cvX, y: 4.3, w: 0.5, h: 0.5,
    fontSize: 14, fontFace: "Georgia",
    color: COLORS.white, bold: true, align: "center", valign: "middle", margin: 0
  });
  slide8.addText(cv.text, {
    x: cvX + 0.6, y: 4.35, w: 2.3, h: 0.4,
    fontSize: 12, fontFace: "Microsoft YaHei",
    color: COLORS.dark, margin: 0
  });
});

// ============================================================
// 第9页：推广价值
// ============================================================
let slide9 = pres.addSlide();
slide9.background = { color: COLORS.white };

slide9.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 1.0,
  fill: { color: COLORS.primary }
});
slide9.addText("推广价值", {
  x: 0.5, y: 0.25, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});

slide9.addText("可复制推广场景", {
  x: 0.5, y: 1.15, w: 3, h: 0.35,
  fontSize: 16, fontFace: "Microsoft YaHei",
  color: COLORS.primary, bold: true, margin: 0
});

const scenarios = [
  { name: "综合执法领域", customer: "各省市城管执法局", value: "全国城管执法改革同步需求" },
  { name: "工程质检领域", customer: "各省市住建/质监站", value: "建筑安全监管全国统一要求" },
  { name: "应急管理领域", customer: "省市县应急管理部门", value: "危化品、矿山等监管" },
  { name: "市场监管领域", customer: "工商、食药监局", value: "放管服改革下的智慧监管" }
];

scenarios.forEach((s, i) => {
  const y = 1.6 + i * 0.7;

  slide9.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: y, w: 9, h: 0.6,
    fill: { color: COLORS.white },
    line: { color: COLORS.lightGray, width: 1 },
    shadow: makeCardShadow()
  });

  slide9.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: y, w: 0.06, h: 0.6,
    fill: { color: COLORS.accent }
  });

  slide9.addText(s.name, {
    x: 0.7, y: y + 0.1, w: 1.8, h: 0.4,
    fontSize: 13, fontFace: "Microsoft YaHei",
    color: COLORS.primary, bold: true, margin: 0
  });

  slide9.addText("适用：" + s.customer, {
    x: 2.6, y: y + 0.15, w: 2.5, h: 0.3,
    fontSize: 11, fontFace: "Microsoft YaHei",
    color: COLORS.gray, margin: 0
  });

  slide9.addText("> " + s.value, {
    x: 5.2, y: y + 0.15, w: 4.1, h: 0.3,
    fontSize: 11, fontFace: "Microsoft YaHei",
    color: COLORS.secondary, margin: 0
  });
});

// 市场机会
slide9.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 4.5, w: 9, h: 1.0,
  fill: { color: COLORS.secondary },
  shadow: makeCardShadow()
});

slide9.addText("市场机会", {
  x: 0.7, y: 4.6, w: 1.5, h: 0.3,
  fontSize: 14, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});

slide9.addText([
  { text: "- 全国住建系统信息化建设需求旺盛", options: { breakLine: true } },
  { text: "- 知识图谱技术在政务领域加速落地", options: { breakLine: true } },
  { text: "- 东方金信 + 腾讯云联合推广优势" }
], {
  x: 0.7, y: 4.95, w: 8.5, h: 0.5,
  fontSize: 11, fontFace: "Microsoft YaHei",
  color: COLORS.white, margin: 0
});

// ============================================================
// 第10页：后续推进计划
// ============================================================
let slide10 = pres.addSlide();
slide10.background = { color: COLORS.white };

slide10.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 1.0,
  fill: { color: COLORS.primary }
});
slide10.addText("后续推进计划", {
  x: 0.5, y: 0.25, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});

// 时间轴线
slide10.addShape(pres.shapes.LINE, {
  x: 1.2, y: 1.6, w: 7.6, h: 0,
  line: { color: COLORS.lightGray, width: 3 }
});

const phases = [
  { period: "近期", time: "1-3个月", title: "海南省住建知识库一期", content: "综合执法、工程监管核心业务覆盖", investment: "约300万" },
  { period: "中期", time: "3-6个月", title: "全省推广与能力扩展", content: "市县全覆盖 + 领域扩展 + 生态对接", investment: "约700万" },
  { period: "远期", time: "6-12个月", title: "跨省复制与行业标准化", content: "形成省级标杆案例 + 全国推广", investment: "千万级" }
];

phases.forEach((phase, i) => {
  const x = 1.2 + i * 3.2;

  slide10.addShape(pres.shapes.OVAL, {
    x: x + 0.9, y: 1.4, w: 0.4, h: 0.4,
    fill: { color: COLORS.accent }
  });

  slide10.addText(phase.period, {
    x: x, y: 1.85, w: 1.2, h: 0.3,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: COLORS.primary, bold: true, align: "center", margin: 0
  });
  slide10.addText(phase.time, {
    x: x, y: 2.1, w: 1.2, h: 0.25,
    fontSize: 10, fontFace: "Microsoft YaHei",
    color: COLORS.gray, align: "center", margin: 0
  });

  slide10.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 2.45, w: 2.9, h: 1.6,
    fill: { color: COLORS.white },
    line: { color: COLORS.lightGray, width: 1 },
    shadow: makeCardShadow()
  });

  slide10.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 2.45, w: 2.9, h: 0.06,
    fill: { color: i === 0 ? COLORS.accent : i === 1 ? COLORS.secondary : COLORS.primary }
  });

  slide10.addText(phase.title, {
    x: x + 0.15, y: 2.58, w: 2.6, h: 0.35,
    fontSize: 12, fontFace: "Microsoft YaHei",
    color: COLORS.primary, bold: true, margin: 0
  });

  slide10.addText(phase.content, {
    x: x + 0.15, y: 2.95, w: 2.6, h: 0.5,
    fontSize: 10, fontFace: "Microsoft YaHei",
    color: COLORS.dark, margin: 0
  });

  slide10.addText("预期投入：" + phase.investment, {
    x: x + 0.15, y: 3.55, w: 2.6, h: 0.3,
    fontSize: 10, fontFace: "Microsoft YaHei",
    color: COLORS.success, bold: true, margin: 0
  });
});

// 项目价值说明
slide10.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 4.3, w: 9, h: 1.15,
  fill: { color: COLORS.light },
  shadow: makeCardShadow()
});

slide10.addText("项目价值", {
  x: 0.7, y: 4.45, w: 2, h: 0.3,
  fontSize: 14, fontFace: "Microsoft YaHei",
  color: COLORS.primary, bold: true, margin: 0
});

slide10.addText([
  { text: "- 树立省级标杆，为全省推广奠定基础", options: { breakLine: true } },
  { text: "- 沉淀可复制的知识图谱建设方法论", options: { breakLine: true } },
  { text: "- 积累政务知识图谱落地经验，形成海南模式" }
], {
  x: 0.7, y: 4.8, w: 8.5, h: 0.6,
  fontSize: 11, fontFace: "Microsoft YaHei",
  color: COLORS.dark, margin: 0
});

// ============================================================
// 第11页：合作模式
// ============================================================
let slide11 = pres.addSlide();
slide11.background = { color: COLORS.white };

slide11.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 1.0,
  fill: { color: COLORS.primary }
});
slide11.addText("合作模式", {
  x: 0.5, y: 0.25, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, margin: 0
});

slide11.addText("灵活的合作模式，适配不同客户需求", {
  x: 0.5, y: 1.15, w: 9, h: 0.35,
  fontSize: 16, fontFace: "Microsoft YaHei",
  color: COLORS.secondary, align: "center", margin: 0
});

const modes = [
  { name: "整体解决方案", desc: "知识库+引擎+应用\n一站式交付", price: "300-500万", suitable: "新建项目" },
  { name: "知识库建设", desc: "仅住建知识库建设\n对接现有平台", price: "150-200万", suitable: "已有平台" },
  { name: "能力赋能", desc: "AI能力接入\n现有系统集成", price: "80-150万", suitable: "集成需求" },
  { name: "联合运营", desc: "长期运营服务\n持续知识更新", price: "年度服务费", suitable: "持续服务" }
];

modes.forEach((mode, i) => {
  const x = 0.5 + i * 2.35;

  slide11.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.7, w: 2.2, h: 3.2,
    fill: { color: COLORS.white },
    line: { color: COLORS.lightGray, width: 1 },
    shadow: makeCardShadow()
  });

  const modeColors = [COLORS.accent, COLORS.secondary, COLORS.primary, COLORS.success];
  slide11.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.7, w: 2.2, h: 0.7,
    fill: { color: modeColors[i] }
  });

  slide11.addText(mode.name, {
    x: x, y: 1.75, w: 2.2, h: 0.6,
    fontSize: 13, fontFace: "Microsoft YaHei",
    color: COLORS.white, bold: true, align: "center", valign: "middle", margin: 0
  });

  slide11.addText(mode.desc, {
    x: x + 0.15, y: 2.55, w: 1.9, h: 0.9,
    fontSize: 11, fontFace: "Microsoft YaHei",
    color: COLORS.dark, align: "center", margin: 0
  });

  slide11.addShape(pres.shapes.LINE, {
    x: x + 0.3, y: 3.5, w: 1.6, h: 0,
    line: { color: COLORS.lightGray, width: 1 }
  });

  slide11.addText("参考报价", {
    x: x, y: 3.65, w: 2.2, h: 0.25,
    fontSize: 9, fontFace: "Microsoft YaHei",
    color: COLORS.gray, align: "center", margin: 0
  });
  slide11.addText(mode.price, {
    x: x, y: 3.9, w: 2.2, h: 0.4,
    fontSize: 14, fontFace: "Georgia",
    color: COLORS.warning, bold: true, align: "center", margin: 0
  });

  slide11.addText("适用：" + mode.suitable, {
    x: x, y: 4.4, w: 2.2, h: 0.35,
    fontSize: 10, fontFace: "Microsoft YaHei",
    color: COLORS.secondary, align: "center", margin: 0
  });
});

// ============================================================
// 第12页：感谢页
// ============================================================
let slide12 = pres.addSlide();
slide12.background = { color: COLORS.primary };

slide12.addShape(pres.shapes.OVAL, {
  x: -2, y: 2, w: 5, h: 5,
  fill: { color: COLORS.secondary, transparency: 70 }
});
slide12.addShape(pres.shapes.OVAL, {
  x: 7, y: -1, w: 4, h: 4,
  fill: { color: COLORS.accent, transparency: 70 }
});

slide12.addText("感谢聆听", {
  x: 0, y: 1.8, w: 10, h: 0.9,
  fontSize: 48, fontFace: "Microsoft YaHei",
  color: COLORS.white, bold: true, align: "center"
});

slide12.addText("期待与您深入合作", {
  x: 0, y: 2.8, w: 10, h: 0.5,
  fontSize: 20, fontFace: "Microsoft YaHei",
  color: COLORS.accent, align: "center"
});

slide12.addShape(pres.shapes.RECTANGLE, {
  x: 3.5, y: 3.5, w: 3, h: 0.02,
  fill: { color: COLORS.accent }
});

slide12.addText("北京东方金信科技股份有限公司", {
  x: 0, y: 4.0, w: 10, h: 0.4,
  fontSize: 16, fontFace: "Microsoft YaHei",
  color: COLORS.white, align: "center"
});

slide12.addText("数据研究院 / 数据库事业部", {
  x: 0, y: 4.45, w: 10, h: 0.35,
  fontSize: 14, fontFace: "Microsoft YaHei",
  color: COLORS.lightGray, align: "center"
});

slide12.addText("www.seaboxdata.com", {
  x: 0, y: 4.85, w: 10, h: 0.35,
  fontSize: 14, fontFace: "Microsoft YaHei",
  color: COLORS.accent, align: "center"
});

// 保存文件
pres.writeFile({ fileName: "海南省住建AI解决方案.pptx" })
  .then(() => {
    console.log("PPT已成功生成：海南省住建AI解决方案.pptx");
  })
  .catch(err => {
    console.error("生成PPT时出错：", err);
  });