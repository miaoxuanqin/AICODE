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

# Neo4j 导入（可选，未安装时优雅降级）
try:
    from app.services.neo4j_service import get_neo4j_service, Neo4jService
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    get_neo4j_service = None


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
        print(f"[DEBUG] build_graph called with {len(graph_entities)} entities, {len(unique_items[:6])} search_results")
        nodes, edges = self.build_graph(graph_entities, unique_items[:6])
        print(f"[DEBUG] build_graph returned {len(nodes)} nodes, {len(edges)} edges")

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

    def _generate_answer(self, question: str, search_results: List[Dict], graph_context: str = "") -> str:
        """生成最终回答"""
        # 构建 Prompt
        prompt = f"""你是住建领域知识助手。请根据以下知识内容回答用户问题。

用户问题：{question}

知识内容：
"""

        for i, item in enumerate(search_results[:5], 1):
            content = item.get("content", "") or item.get("summary", "")
            prompt += f"\n【知识 {i}】{item.get('title', '')}\n{content[:500]}\n"

        # 如果有图谱上下文，添加到 prompt 中
        if graph_context:
            prompt += f"\n{graph_context}\n"

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

    def _build_graph_context(self, neo4j_context: Dict[str, Any], entities: List[Dict]) -> str:
        """
        从 Neo4j 上下文构建可读的图谱描述，用于补充 LLM 回答

        Args:
            neo4j_context: Neo4j 查询结果（包含 nodes, edges）
            entities: 原始识别的实体列表

        Returns:
            可读性好、可直接加入 prompt 的图谱描述字符串
        """
        if not neo4j_context.get("available"):
            return ""

        nodes = neo4j_context.get("nodes", [])
        edges = neo4j_context.get("edges", [])

        if not nodes:
            return ""

        lines = ["\n=== 知识图谱关系（供参考）===\n"]

        # 按节点 label 分组，便于理解
        label_groups = {}
        for node in nodes:
            label = node.get("label", "Unknown")
            name = node.get("name", "")
            if name:
                if label not in label_groups:
                    label_groups[label] = []
                label_groups[label].append(name)

        # 输出分类后的实体
        if label_groups:
            lines.append("【实体分类】")
            for label, names in label_groups.items():
                label_display = {
                    "Law": "法规",
                    "Article": "条款",
                    "Standard": "标准",
                    "Penalty": "处罚",
                    "Case": "案例",
                    "Subject": "主体",
                    "Behavior": "行为"
                }.get(label, label)
                lines.append(f"  {label_display}：{', '.join(names[:5])}")

        # 输出关系链
        if edges:
            lines.append("\n【关系链条】")
            for edge in edges[:10]:  # 限制关系数量
                source = edge.get("source", "")
                target = edge.get("target", "")
                relation = edge.get("type", "相关")

                # 找到对应的 node name
                source_name = next((n.get("name", "") for n in nodes if n.get("id") == source), source)
                target_name = next((n.get("name", "") for n in nodes if n.get("id") == target), target)

                # 转换关系名称
                relation_display = {
                    "CONTAINS": "包含",
                    "REFERS": "引用",
                    "DEFINES": "规定",
                    "TRIGGERS": "触发",
                    "APPLIES": "适用于",
                    "INVOLVES": "涉及",
                    "IMPOSES": "施加",
                    "相关规定于": "相关规定于",
                    "触发": "触发",
                    "涉及": "涉及"
                }.get(relation, relation)

                lines.append(f"  • {source_name} {relation_display} {target_name}")

        # 输出简要总结
        lines.append(f"\n（以上图谱包含 {len(nodes)} 个实体和 {len(edges)} 条关系）")

        return "\n".join(lines)

    # ==================== Neo4j 集成方法 ====================

    def _query_neo4j_context(self, entities: List[Dict]) -> Dict[str, Any]:
        """
        查询 Neo4j 获取关联上下文

        Args:
            entities: 实体列表 [{"text": "...", "type": "..."}]

        Returns:
            包含 nodes, edges, paths 的字典
        """
        if not NEO4J_AVAILABLE:
            return {"nodes": [], "edges": [], "paths": [], "available": False}

        try:
            neo4j = get_neo4j_service()
            if not neo4j.verify_connectivity():
                print("Neo4j 连接不可用")
                return {"nodes": [], "edges": [], "paths": [], "available": False}

            all_nodes = []
            all_edges = []
            all_paths = []

            # 查询每个实体的关联
            for entity in entities[:5]:
                entity_name = entity.get("text", "")
                if not entity_name:
                    continue

                # 尝试多种匹配方式（处理书名号差异）
                matched_name = self._match_neo4j_entity(entity_name, neo4j)
                if matched_name:
                    entity_name = matched_name

                # 获取子图
                subgraph = neo4j.get_subgraph(entity_name, depth=2)
                if subgraph:
                    all_nodes.extend(subgraph.get("nodes", []))
                    all_edges.extend(subgraph.get("edges", []))

                # 查找与其他实体的路径
                for entity2 in entities:
                    if entity2.get("text") != entity_name:
                        paths = neo4j.find_paths(entity_name, entity2.get("text", ""))
                        all_paths.extend(paths)

            # 去重
            unique_nodes = self._deduplicate_nodes(all_nodes)
            unique_edges = self._deduplicate_edges(all_edges)

            return {
                "nodes": unique_nodes,
                "edges": unique_edges,
                "paths": all_paths,
                "available": True
            }

        except Exception as e:
            print(f"Neo4j 查询失败: {e}")
            return {"nodes": [], "edges": [], "paths": [], "available": False, "error": str(e)}

    def _deduplicate_nodes(self, nodes: List[Dict]) -> List[Dict]:
        """去重节点"""
        seen = set()
        unique = []
        for node in nodes:
            node_id = node.get("id", "")
            if node_id and node_id not in seen:
                seen.add(node_id)
                unique.append(node)
        return unique

    def _deduplicate_edges(self, edges: List[Dict]) -> List[Dict]:
        """去重边"""
        seen = set()
        unique = []
        for edge in edges:
            edge_id = f"{edge.get('source')}-{edge.get('type')}-{edge.get('target')}"
            if edge_id not in seen:
                seen.add(edge_id)
                unique.append(edge)
        return unique

    def _match_neo4j_entity(self, entity_name: str, neo4j) -> Optional[str]:
        """
        匹配 Neo4j 中的实体名称（处理书名号差异）

        Args:
            entity_name: 原始实体名称
            neo4j: Neo4j 服务实例

        Returns:
            匹配到的实体名称，如果没匹配到返回 None
        """
        # 尝试原始名称
        if self._neo4j_entity_exists(entity_name, neo4j):
            return entity_name

        # 尝试添加书名号
        if not entity_name.startswith('《'):
            with_bracket = f"《{entity_name}》"
            if self._neo4j_entity_exists(with_bracket, neo4j):
                return with_bracket

        # 尝试去掉书名号
        if entity_name.startswith('《'):
            without_bracket = entity_name[1:].rstrip('》')
            if self._neo4j_entity_exists(without_bracket, neo4j):
                return without_bracket

        return None

    def _neo4j_entity_exists(self, entity_name: str, neo4j) -> bool:
        """检查实体是否存在于 Neo4j"""
        try:
            with neo4j.driver.session() as session:
                result = session.run(
                    "MATCH (n {name: $name}) RETURN count(n) as cnt",
                    name=entity_name
                )
                record = result.single()
                return record[0] > 0 if record else False
        except Exception:
            return False

    def _build_graph_from_neo4j(
        self,
        neo4j_context: Dict[str, Any],
        question: str
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        从 Neo4j 上下文构建图谱数据

        Args:
            neo4j_context: Neo4j 查询结果
            question: 用户问题

        Returns:
            (nodes, edges) 元组
        """
        nodes = []
        edges = []
        node_id_map = {}

        if not neo4j_context.get("available"):
            # Neo4j 不可用，返回空
            return nodes, edges

        neo4j_nodes = neo4j_context.get("nodes", [])
        neo4j_edges = neo4j_context.get("edges", [])

        # 添加问题节点
        question_node = {
            "id": "q1",
            "label": question[:20],
            "type": "question",
            "description": "",
            "attributes": []
        }
        nodes.append(question_node)
        node_id_map["q1"] = 0

        # 添加 Neo4j 节点
        node_idx = 1
        for neo4j_node in neo4j_nodes[:10]:  # 限制节点数量
            node_id = f"n{node_idx}"
            node = {
                "id": node_id,
                "label": neo4j_node.get("name", "")[:20],
                "type": self._map_neo4j_label_to_type(neo4j_node.get("label", "")),
                "description": "",
                "attributes": []
            }
            nodes.append(node)
            node_id_map[neo4j_node.get("id", "")] = node_idx
            node_idx += 1

        # 添加边
        edge_idx = 1
        for neo4j_edge in neo4j_edges[:15]:  # 限制边数量
            source_id = neo4j_edge.get("source", "")
            target_id = neo4j_edge.get("target", "")

            if source_id in node_id_map and target_id in node_id_map:
                edges.append({
                    "id": f"e{edge_idx}",
                    "source": node_id_map[source_id],
                    "target": node_id_map[target_id],
                    "label": neo4j_edge.get("type", "相关")
                })
                edge_idx += 1

        # 布局计算
        self._layout_nodes(nodes)

        return nodes, edges

    def _map_neo4j_label_to_type(self, label: str) -> str:
        """将 Neo4j 标签映射为前端类型"""
        mapping = {
            "Law": "law",
            "Article": "article",
            "Standard": "standard",
            "Penalty": "penalty",
            "Case": "case",
            "Subject": "subject",
            "Behavior": "behavior"
        }
        return mapping.get(label, "law")

    def reason_with_neo4j(
        self,
        question: str,
        user_id: str = None,
        db=None
    ) -> Dict[str, Any]:
        """
        使用 Neo4j 增强的图谱推理问答

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

        # Step 3: Neo4j 图谱推理（替代原来的关系扩展）
        neo4j_context = self._query_neo4j_context(step1_entities)

        if neo4j_context.get("available") and len(neo4j_context.get("nodes", [])) > 0:
            reasoning_chain.append({
                "step": 3,
                "query": "Neo4j 图谱推理",
                "result": f"找到 {len(neo4j_context.get('nodes', []))} 个关联实体",
                "entities": [],
                "details": {
                    "search_query": "",
                    "knowledge_found": [n.get("name", "") for n in neo4j_context.get("nodes", [])[:5]]
                }
            })

            # 构建图谱数据
            nodes, edges = self._build_graph_from_neo4j(neo4j_context, question)
            graph_data = {"nodes": nodes, "edges": edges}
        else:
            # Fallback: 使用原来的扩展逻辑
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

            # 构建图谱数据（使用原来的方式）
            graph_entities = step1_entities if step1_entities else [{"text": question[:20], "type": "question"}]
            nodes, edges = self.build_graph(graph_entities, all_search_items[:6])
            graph_data = {"nodes": nodes, "edges": edges}

        # Step 4: 构建图谱上下文（用于 LLM）
        graph_context = self._build_graph_context(neo4j_context, step1_entities) if neo4j_context.get("available") else ""

        # Step 5: 去重
        seen_ids = set()
        unique_items = []
        for item in all_search_items:
            if item.get("id") not in seen_ids:
                seen_ids.add(item.get("id"))
                unique_items.append(item)

        reasoning_chain.append({
            "step": 5,
            "query": "整合知识并生成回答",
            "result": f"整合 {len(unique_items)} 条知识进行回答",
            "entities": [],
            "details": {
                "search_query": "",
                "knowledge_found": [item.get("title", "") for item in unique_items]
            }
        })

        # Step 6: 生成回答（传入图谱上下文）
        if unique_items:
            final_answer = self._generate_answer(question, unique_items, graph_context)
        else:
            final_answer = "抱歉，知识库中没有找到与您问题相关的内容。"

        # Step 6: 构建引用来源
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


graph_service = GraphService()