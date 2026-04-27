"""
知识图谱服务 (Graph Service)
基于知识库构建实体关系图谱，支持多跳推理问答
"""
import uuid
import re
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

import anthropic

from app.config import get_settings
from app.services.search_service import search_service
from app.services.embedding_service import embedding_service

settings = get_settings()


class GraphNode:
    """图谱节点"""
    def __init__(self, id: str, label: str, node_type: str,
                 description: str = "", attributes: List[Dict] = None):
        self.id = id
        self.label = label
        self.type = node_type
        self.description = description
        self.attributes = attributes or []
        self.x = 0
        self.y = 0


class GraphEdge:
    """图谱边"""
    def __init__(self, id: str, source: str, target: str, label: str):
        self.id = id
        self.source = source
        self.target = target
        self.label = label


class GraphService:
    """知识图谱服务"""

    def __init__(self):
        self._llm_client = None
        self.entity_patterns = {
            "law": ["条例", "法规", "法律", "办法", "规定", "标准", "规范"],
            "case": ["事故", "案例", "案件", "处罚", "违法"],
            "policy": ["通知", "意见", "决定", "公告", "政策"],
            "article": [r"第\d+条", r"第\d+款", r"第\d+项"],
            "penalty": ["罚款", "处罚", "刑事责任", "行政处分"],
            "standard": ["标准", "规范", "规程", "指标"]
        }

    @property
    def llm_client(self):
        """延迟初始化 LLM 客户端"""
        if self._llm_client is None:
            self._llm_client = anthropic.Anthropic(
                base_url=settings.anthropic_base_url,
                api_key=settings.anthropic_auth_token,
            )
        return self._llm_client

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """从文本中提取实体和类型"""
        entities = []

        # 使用规则匹配已知实体类型
        for entity_type, keywords in self.entity_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    # 尝试找到完整的实体名称
                    pattern = rf'{keyword}[^，。！？、\n]{{0,30}}'
                    matches = re.findall(pattern, text)
                    for match in matches:
                        if match and len(match) > len(keyword):
                            entities.append({
                                "text": match.strip(),
                                "type": entity_type
                            })

        # 使用 LLM 辅助提取关键实体
        try:
            llm_entities = self._extract_entities_with_llm(text)
            for ent in llm_entities:
                if ent not in [e["text"] for e in entities]:
                    entities.append(ent)
        except Exception as e:
            print(f"LLM 实体提取失败: {e}")

        return entities[:10]  # 限制实体数量

    def _extract_entities_with_llm(self, text: str) -> List[Dict[str, str]]:
        """使用 LLM 提取实体"""
        prompt = f"""从以下文本中提取关键实体及其类型。返回JSON数组格式：
[{{"text": "实体名称", "type": "实体类型"}}]

实体类型包括：law(法规)、case(案例)、policy(政策)、article(条款)、penalty(处罚)、standard(标准)、person(人物)、org(组织)

文本内容：
{text[:1000]}

请只返回实体列表，不要其他内容。"""

        try:
            message = self.llm_client.messages.create(
                model=settings.anthropic_default_haiku_model,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    result_text = block.text
                    break

            # 解析 JSON
            import json
            json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
            if json_match:
                entities = json.loads(json_match.group())
                return entities
        except Exception as e:
            print(f"LLM 实体解析失败: {e}")

        return []

    def build_graph(self, entities: List[Dict], search_results: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """根据实体和搜索结果构建图谱"""
        nodes = []
        edges = []
        node_id_map = {}  # 用于去重和关联

        # 添加问题节点
        question_node = {
            "id": "q1",
            "label": entities[0]["text"] if entities else "问题",
            "type": "question",
            "description": "",
            "attributes": []
        }
        nodes.append(question_node)
        node_id_map["q1"] = len(nodes) - 1

        # 为每个实体创建节点
        for idx, entity in enumerate(entities[:6]):
            node_id = f"n{idx + 1}"
            node = {
                "id": node_id,
                "label": entity["text"][:20],
                "type": entity["type"],
                "description": "",
                "attributes": []
            }
            nodes.append(node)
            node_id_map[node_id] = len(nodes) - 1

            # 添加问题到实体的边
            edges.append({
                "id": f"e{idx * 2 + 1}",
                "source": "q1",
                "target": node_id,
                "label": "涉及"
            })

        # 根据搜索结果添加法规和案例节点
        knowledge_idx = len(nodes)
        for item in search_results[:4]:
            node_id = f"k{knowledge_idx}"
            category = item.get("category", "tech")
            node = {
                "id": node_id,
                "label": item.get("title", "")[:15],
                "type": category,
                "description": item.get("summary", "")[:50],
                "attributes": []
            }
            nodes.append(node)
            node_id_map[node_id] = len(nodes) - 1

            # 建立关联边
            if entities:
                # 关联到第一个实体
                first_entity_idx = min(1, len(entities))
                entity_node_id = f"n{first_entity_idx}"
                if entity_node_id in node_id_map:
                    edges.append({
                        "id": f"ek{knowledge_idx}",
                        "source": entity_node_id,
                        "target": node_id,
                        "label": "相关"
                    })

            knowledge_idx += 1

        # 计算节点位置（简单布局）
        self._layout_nodes(nodes)

        return nodes, edges

    def _layout_nodes(self, nodes: List[Dict]):
        """计算节点布局位置"""
        if not nodes:
            return

        # 中心点
        center_x = 200
        center_y = 50

        # 问题节点在顶部
        nodes[0]["x"] = center_x
        nodes[0]["y"] = center_y

        # 其他节点围绕中心分布
        import math
        node_count = len(nodes) - 1
        if node_count > 0:
            radius = 120
            for i in range(node_count):
                angle = 2 * math.pi * i / node_count - math.pi / 2
                nodes[i + 1]["x"] = center_x + radius * math.cos(angle)
                nodes[i + 1]["y"] = center_y + 130 + radius * 0.6 * math.sin(angle)

    def reason(self, question: str, user_id: str = None, db=None) -> Dict[str, Any]:
        """
        执行图谱增强推理问答

        Args:
            question: 用户问题
            user_id: 用户ID
            db: 数据库会话

        Returns:
            包含 answer, reasoning_chain, graph_data, citations 的字典
        """
        reasoning_chain = []
        all_search_items = []
        final_answer = ""

        # Step 1: 实体识别
        step1_entities = self.extract_entities(question)
        reasoning_chain.append({
            "step": 1,
            "query": "理解问题并识别关键实体",
            "result": f"识别到 {len(step1_entities)} 个关键实体",
            "entities": [e["text"] for e in step1_entities[:5]],
            "details": {
                "search_query": question,
                "knowledge_found": []
            }
        })

        # Step 2: 第一次搜索 - 精确匹配
        first_query = question
        try:
            query_vector = embedding_service.encode_single(first_query)
            knowledge_ids = search_service.search_vector(
                query_vector=query_vector,
                user_id=user_id or "anonymous",
                limit=6
            )
            items = []
            for kid in knowledge_ids:
                doc = search_service.get_by_id(kid)
                if doc:
                    items.append(doc)
            first_results = {"items": items, "total": len(items)}
        except Exception as e:
            print(f"向量搜索失败: {e}")
            first_results = search_service.search_keyword(
                query=first_query,
                user_id=user_id or "anonymous",
                page=1,
                page_size=6
            )

        reasoning_chain.append({
            "step": 2,
            "query": "检索相关知识库内容",
            "result": f"找到 {first_results['total']} 条相关知识",
            "entities": [],
            "details": {
                "search_query": first_query,
                "knowledge_found": [item.get("title", "") for item in first_results.get("items", [])]
            }
        })

        all_search_items.extend(first_results.get("items", []))

        # Step 3: 关系扩展 - 搜索相关内容
        expand_query = self._generate_expand_query(question, first_results.get("items", []))
        if expand_query and expand_query != first_query:
            try:
                query_vector = embedding_service.encode_single(expand_query)
                knowledge_ids = search_service.search_vector(
                    query_vector=query_vector,
                    user_id=user_id or "anonymous",
                    limit=4
                )
                items = []
                for kid in knowledge_ids:
                    doc = search_service.get_by_id(kid)
                    if doc:
                        items.append(doc)
                second_results = {"items": items, "total": len(items)}
            except Exception:
                second_results = search_service.search_keyword(
                    query=expand_query,
                    user_id=user_id or "anonymous",
                    page=1,
                    page_size=4
                )

            reasoning_chain.append({
                "step": 3,
                "query": "扩展关联知识",
                "result": f"补充找到 {second_results['total']} 条关联知识",
                "entities": [],
                "details": {
                    "search_query": expand_query,
                    "knowledge_found": [item.get("title", "") for item in second_results.get("items", [])]
                }
            })
            all_search_items.extend(second_results.get("items", []))
        else:
            reasoning_chain.append({
                "step": 3,
                "query": "扩展关联知识",
                "result": "无需扩展",
                "entities": [],
                "details": {
                    "search_query": "",
                    "knowledge_found": []
                }
            })

        # Step 4: 去重
        seen_ids = set()
        unique_items = []
        for item in all_search_items:
            if item.get("id") not in seen_ids:
                seen_ids.add(item.get("id"))
                unique_items.append(item)

        reasoning_chain.append({
            "step": 4,
            "query": "整合知识并生成回答",
            "result": f"整合 {len(unique_items)} 条知识进行回答",
            "entities": [],
            "details": {
                "search_query": "",
                "knowledge_found": [item.get("title", "") for item in unique_items]
            }
        })

        # Step 5: 构建图谱数据
        graph_entities = step1_entities if step1_entities else [{"text": question[:20], "type": "question"}]
        nodes, edges = self.build_graph(graph_entities, unique_items[:6])

        graph_data = {
            "nodes": nodes,
            "edges": edges
        }

        # Step 6: 生成回答
        if unique_items:
            final_answer = self._generate_answer(question, unique_items)
        else:
            final_answer = "抱歉，知识库中没有找到与您问题相关的内容。"

        # Step 7: 构建引用来源
        citations = []
        for item in unique_items[:5]:
            category = item.get("category", "tech")
            type_names = {
                "law": "法规",
                "case": "案例",
                "policy": "政策",
                "tech": "技术",
                "article": "条款"
            }
            citations.append({
                "id": item.get("id", ""),
                "type": category,
                "typeName": type_names.get(category, "知识"),
                "title": item.get("title", "")
            })

        return {
            "answer": final_answer,
            "reasoning_chain": reasoning_chain,
            "graph_data": graph_data,
            "citations": citations
        }

    def _generate_expand_query(self, original_query: str, search_results: List[Dict]) -> str:
        """生成扩展查询"""
        if not search_results:
            return ""

        # 提取搜索结果中的关键主题
        topics = []
        for item in search_results[:3]:
            title = item.get("title", "")
            if title:
                # 提取标题中的关键名词
                words = re.findall(r'[一-龥]{2,}', title)
                topics.extend(words[:2])

        if topics:
            return "、".join(topics[:5])
        return ""

    def _generate_answer(self, question: str, search_results: List[Dict]) -> str:
        """生成最终回答"""
        # 构建 Prompt
        prompt = f"""你是住建领域知识助手。请根据以下知识内容回答用户问题。

用户问题：{question}

知识内容：
"""

        for i, item in enumerate(search_results[:5], 1):
            content = item.get("content", "") or item.get("summary", "")
            prompt += f"\n【知识 {i}】{item.get('title', '')}\n{content[:500]}\n"

        prompt += """
请给出专业、准确的回答。如果知识不足以回答，请说明。
回答格式：先给出核心答案，然后详细说明依据。
"""

        try:
            message = self.llm_client.messages.create(
                model=settings.anthropic_default_haiku_model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            for block in message.content:
                if hasattr(block, 'text'):
                    return block.text

            return "抱歉，回答生成失败"

        except Exception as e:
            print(f"LLM 调用失败: {e}")
            return "服务暂时不可用"


graph_service = GraphService()