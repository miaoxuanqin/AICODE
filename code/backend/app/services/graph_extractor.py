"""
实体关系抽取服务
从知识文本中抽取实体和关系，写入 Neo4j
"""
import re
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

import anthropic

from app.config import get_settings
from app.services.neo4j_service import get_neo4j_service

settings = get_settings()


@dataclass
class ExtractedEntity:
    """抽取的实体"""
    name: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedRelation:
    """抽取的关系"""
    from_name: str
    to_name: str
    rel_type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """抽取结果"""
    entities: List[ExtractedEntity]
    relations: List[ExtractedRelation]


class GraphExtractor:
    """实体关系抽取器"""

    # 实体类型映射
    ENTITY_TYPES = {
        "Law": "法规",
        "Article": "条款",
        "Standard": "标准",
        "Penalty": "处罚",
        "Case": "案例",
        "Subject": "主体",
        "Behavior": "行为"
    }

    # 关系类型映射
    RELATION_TYPES = {
        "CONTAINS": "包含",
        "REFERS": "引用",
        "DEFINES": "规定",
        "TRIGGERS": "触发",
        "APPLIES": "适用",
        "INVOLVES": "涉及",
        "IMPOSES": "施加"
    }

    # 关键词匹配规则
    ENTITY_PATTERNS = {
        "Law": [
            r'《[^》]+》',
            r'(?:噪声|大气|水|土壤|固废|辐射|建筑|施工|安全|消防|环保|质量)污染防治(?:法|条例|规定|办法)',
            r'(?:建设工程|建筑|施工|园林|市政|房地产)(?:管理条例?|规定|办法|标准)',
        ],
        "Article": [
            r'第[一二三四五六七八九十百千万\d]+[条款项]',
            r'第[一二三四五六七八九十百千万\d]+[条]',
            r'(?:第\d+款)',
        ],
        "Standard": [
            r'(?:GB|TJ|JGJ|CJJ|DB|QB)[-\s]?\d+[^\s,，；]*(?:标准|规范|规程)?',
            r'(?:声环境|空气质量|建筑|施工|安全|环保|质量)标准',
        ],
        "Penalty": [
            r'处以?(?:罚款?|处罚?)[^，。；\n]{0,50}?(?:\d+[,，]?\d*(?:\.\d+)?(?:万|千|百|元)?)',
            r'(?:责令|处以)(?:改正|停产|停业|吊销|警告)',
            r'(?:罚款|处罚)(?:金额)?[^\n]{0,30}(?:\d+[,，]?\d*(?:\.\d+)?(?:万|千|百|元)?)',
        ],
        "Case": [
            r'(?:案例?|案[^例][^件]?[^\n]{0,20})',
            r'(?:处罚|违法|违规|事故)[^\n]{0,30}案例?',
            r'(?:XX|某|\*\*)[^\n]{0,10}项目?[^\n]{0,10}(?:处罚|违法|违规|事故)',
        ],
        "Behavior": [
            r'(?:噪声|废气|废水|固废|辐射|超标|违规|违法|擅自|未按|不符合)[^\s，。；]{0,20}',
            r'(?:夜间|白天|施工|排放|作业|建设)[^\s，。；]{0,15}(?:超标|违规|违法|禁止)',
        ],
        "Subject": [
            r'(?:建设|施工|监理|设计|勘察|检测|验收|监督)单位',
            r'(?:建设|施工|监理|设计)企业',
            r'(?:建设|施工|项目|工程)(?:负责人|主管)?',
        ]
    }

    def __init__(self):
        self._llm_client = None

    @property
    def llm_client(self):
        """延迟初始化 LLM 客户端"""
        if self._llm_client is None:
            self._llm_client = anthropic.Anthropic(
                base_url=settings.anthropic_base_url,
                api_key=settings.anthropic_auth_token,
            )
        return self._llm_client

    def extract(self, knowledge_id: str, text: str) -> ExtractionResult:
        """
        执行实体关系抽取

        Args:
            knowledge_id: 知识ID（用于关联）
            text: 文本内容

        Returns:
            ExtractionResult: 包含实体和关系列表
        """
        # Step 1: 规则快速抽取
        rule_entities, rule_relations = self._rule_extract(text)

        # Step 2: LLM 语义抽取
        llm_result = self._llm_extract(text)

        # Step 3: 合并去重
        entities = self._merge_entities(rule_entities, llm_result.entities)
        relations = self._merge_relations(rule_relations, llm_result.relations)

        # Step 4: 添加知识关联属性
        for entity in entities:
            entity.properties["knowledge_id"] = knowledge_id

        return ExtractionResult(entities=entities, relations=relations)

    def _rule_extract(self, text: str) -> Tuple[List[ExtractedEntity], List[ExtractedRelation]]:
        """规则快速抽取"""
        entities = []
        relations = []

        # 提取各类实体
        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    match = match.strip()
                    if match and len(match) > 2:
                        entity = ExtractedEntity(
                            name=match,
                            type=entity_type,
                            properties={"extracted_by": "rule"}
                        )
                        if entity not in entities:
                            entities.append(entity)

        # 提取关系（基于共现）
        relations = self._extract_relations_by_cooccurrence(text, entities)

        return entities, relations

    def _extract_relations_by_cooccurrence(
        self,
        text: str,
        entities: List[ExtractedEntity]
    ) -> List[ExtractedRelation]:
        """基于共现关系提取"""
        relations = []
        entity_names = [e.name for e in entities]

        # 法规-条款关系
        law_entities = [e for e in entities if e.type == "Law"]
        article_entities = [e for e in entities if e.type == "Article"]

        for law in law_entities:
            for article in article_entities:
                # 检查是否在同一上下文
                if self._in_same_context(text, law.name, article.name):
                    relations.append(ExtractedRelation(
                        from_name=law.name,
                        to_name=article.name,
                        rel_type="CONTAINS",
                        properties={"context": "共现提取"}
                    ))

        # 条款-标准关系
        standard_entities = [e for e in entities if e.type == "Standard"]
        for article in article_entities:
            for standard in standard_entities:
                if self._in_same_context(text, article.name, standard.name):
                    relations.append(ExtractedRelation(
                        from_name=article.name,
                        to_name=standard.name,
                        rel_type="REFERS",
                        properties={"context": "共现提取"}
                    ))

        # 处罚关系
        penalty_entities = [e for e in entities if e.type == "Penalty"]
        for behavior in [e for e in entities if e.type == "Behavior"]:
            for penalty in penalty_entities:
                if self._in_same_context(text, behavior.name, penalty.name):
                    relations.append(ExtractedRelation(
                        from_name=behavior.name,
                        to_name=penalty.name,
                        rel_type="TRIGGERS",
                        properties={"context": "共现提取"}
                    ))

        return relations

    def _in_same_context(self, text: str, entity1: str, entity2: str) -> bool:
        """检查两个实体是否在同一上下文（100字符内）"""
        try:
            idx1 = text.find(entity1)
            idx2 = text.find(entity2)
            if idx1 >= 0 and idx2 >= 0:
                return abs(idx1 - idx2) < 200
        except Exception:
            pass
        return False

    def _llm_extract(self, text: str) -> ExtractionResult:
        """使用 LLM 抽取实体和关系"""
        prompt = self._build_llm_prompt(text)

        try:
            message = self.llm_client.messages.create(
                model=settings.anthropic_default_haiku_model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    result_text = block.text
                    break

            return self._parse_llm_result(result_text)

        except Exception as e:
            print(f"LLM 抽取失败: {e}")
            return ExtractionResult(entities=[], relations=[])

    def _build_llm_prompt(self, text: str) -> str:
        """构建 LLM 抽取 Prompt"""
        return f"""从以下文本中提取关键实体及其类型，以及实体之间的关系。

实体类型说明：
- Law: 法规名称（如《噪声污染防治法》、《建设工程施工现场噪声污染防治法》）
- Article: 条款编号（如第2条、第3条第1款、第5项）
- Standard: 技术标准编号（如GB 3096-2008、GB 50189）
- Penalty: 处罚内容（如罚款5000-50000元、责令停产停业）
- Case: 案例名称（如XX项目噪声超标案）
- Subject: 主体（如建设单位、施工单位、监理单位）
- Behavior: 行为（如噪声超标排放、违规夜间施工）

关系类型说明：
- CONTAINS: 法规包含条款（如"噪声法 CONTAINS 第2条"）
- REFERS: 条款引用标准（如"第2条 REFERS GB 3096"）
- DEFINES: 条款规定行为（如"第2条 DEFINES 噪声排放"）
- TRIGGERS: 行为触发处罚（如"噪声超标 TRIGGERS 罚款"）
- APPLIES: 案例适用条款（如"XX案 APPLIES 第2条"）
- INVOLVES: 案例涉及主体（如"XX案 INVOLVES 施工单位"）

文本内容：
{text[:3000]}

请以JSON格式返回：
{{
  "entities": [
    {{"type": "Law", "name": "实体名称"}},
    {{"type": "Article", "name": "实体名称"}}
  ],
  "relations": [
    {{"from": "实体A", "to": "实体B", "type": "关系类型"}}
  ]
}}

请只返回JSON，不要其他内容："""

    def _parse_llm_result(self, result_text: str) -> ExtractionResult:
        """解析 LLM 返回结果"""
        entities = []
        relations = []

        try:
            # 提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if not json_match:
                return ExtractionResult(entities=[], relations=[])

            data = json.loads(json_match.group())

            # 解析实体
            for item in data.get("entities", []):
                if "type" in item and "name" in item:
                    entities.append(ExtractedEntity(
                        name=item["name"],
                        type=item["type"],
                        properties={"extracted_by": "llm"}
                    ))

            # 解析关系
            for item in data.get("relations", []):
                if all(k in item for k in ["from", "to", "type"]):
                    relations.append(ExtractedRelation(
                        from_name=item["from"],
                        to_name=item["to"],
                        rel_type=item["type"],
                        properties={"extracted_by": "llm"}
                    ))

        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")

        return ExtractionResult(entities=entities, relations=relations)

    def _merge_entities(
        self,
        rule_entities: List[ExtractedEntity],
        llm_entities: List[ExtractedEntity]
    ) -> List[ExtractedEntity]:
        """合并实体，去重"""
        merged = []
        name_map = {}

        # 先添加规则抽取的实体
        for entity in rule_entities:
            if entity.name not in name_map:
                name_map[entity.name] = entity
                merged.append(entity)

        # 合并 LLM 抽取的实体
        for entity in llm_entities:
            if entity.name not in name_map:
                name_map[entity.name] = entity
                merged.append(entity)
            else:
                # 保留两种抽取来源
                existing = name_map[entity.name]
                if "llm" not in existing.properties.get("extracted_by", ""):
                    existing.properties["extracted_by"] += ",llm"

        return merged

    def _merge_relations(
        self,
        rule_relations: List[ExtractedRelation],
        llm_relations: List[ExtractedRelation]
    ) -> List[ExtractedRelation]:
        """合并关系，去重"""
        merged = []
        seen = set()

        for rel in rule_relations + llm_relations:
            key = (rel.from_name, rel.to_name, rel.rel_type)
            if key not in seen:
                seen.add(key)
                merged.append(rel)

        return merged

    def sync_to_neo4j(
        self,
        knowledge_id: str,
        text: str
    ) -> Dict[str, Any]:
        """
        抽取并同步到 Neo4j

        Args:
            knowledge_id: 知识ID
            text: 文本内容

        Returns:
            同步结果统计
        """
        result = self.extract(knowledge_id, text)
        neo4j = get_neo4j_service()

        stats = {
            "entities_total": len(result.entities),
            "relations_total": len(result.relations),
            "entities_created": 0,
            "relations_created": 0
        }

        # 写入节点（带 knowledge_id 引用）
        for entity in result.entities:
            if neo4j.upsert_node(entity.type, entity.name, entity.properties, knowledge_id):
                stats["entities_created"] += 1

        # 写入关系
        for relation in result.relations:
            # 尝试推断标签
            from_label = self._infer_label(relation.from_name, result.entities)
            to_label = self._infer_label(relation.to_name, result.entities)

            if from_label and to_label:
                if neo4j.create_relation(
                    relation.from_name,
                    from_label,
                    relation.to_name,
                    to_label,
                    relation.rel_type,
                    relation.properties
                ):
                    stats["relations_created"] += 1

        return stats

    def delete_from_neo4j(self, knowledge_id: str) -> Dict[str, Any]:
        """
        从 Neo4j 删除与知识关联的实体（只删除无其他引用的实体）

        Args:
            knowledge_id: 知识ID

        Returns:
            删除结果统计
        """
        neo4j = get_neo4j_service()
        return neo4j.remove_knowledge_reference(knowledge_id)

    def _infer_label(
        self,
        name: str,
        entities: List[ExtractedEntity]
    ) -> Optional[str]:
        """推断实体的标签"""
        for entity in entities:
            if entity.name == name:
                return entity.type
        return None

    async def async_sync_to_neo4j(
        self,
        knowledge_id: str,
        text: str
    ) -> Dict[str, Any]:
        """异步同步到 Neo4j"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.sync_to_neo4j,
            knowledge_id,
            text
        )


# 全局单例
_graph_extractor: Optional[GraphExtractor] = None


def get_graph_extractor() -> GraphExtractor:
    """获取抽取器单例"""
    global _graph_extractor
    if _graph_extractor is None:
        _graph_extractor = GraphExtractor()
    return _graph_extractor
