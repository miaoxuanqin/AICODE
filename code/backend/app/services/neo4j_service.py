"""
Neo4j 图数据库服务
提供节点和关系的 CRUD 操作，以及图谱查询功能
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

from app.config import get_settings

settings = get_settings()

# Neo4j driver availability flag
NEO4J_AVAILABLE = True


class Neo4jNodeNotFoundError(Exception):
    """节点不存在"""
    pass


class Neo4jService:
    """Neo4j 操作服务"""

    def __init__(
        self,
        uri: str = None,
        user: str = None,
        password: str = None
    ):
        self.uri = uri or settings.neo4j_uri
        self.user = user or settings.neo4j_user
        self.password = password or settings.neo4j_password
        self._driver = None

    @property
    def driver(self):
        """延迟初始化 Neo4j 驱动"""
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
        return self._driver

    def close(self):
        """关闭连接"""
        if self._driver:
            self._driver.close()
            self._driver = None

    def verify_connectivity(self) -> bool:
        """验证连接是否正常"""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS test")
                return result.single()["test"] == 1
        except (ServiceUnavailable, AuthError) as e:
            print(f"Neo4j 连接失败: {e}")
            return False

    # ==================== 节点操作 ====================

    def upsert_node(
        self,
        label: str,
        name: str,
        properties: Dict[str, Any] = None,
        knowledge_id: str = None
    ) -> bool:
        """
        插入或更新节点（MATCH + SET）

        Args:
            label: 节点标签 (Law, Article, Standard, etc.)
            name: 节点名称（唯一标识）
            properties: 其他属性
            knowledge_id: 关联的知识ID（用于引用计数）

        Returns:
            bool: 操作是否成功
        """
        properties = properties or {}
        properties["name"] = name
        properties["updated_at"] = datetime.now().isoformat()

        # 如果没有 created_at，添加创建时间
        if "created_at" not in properties:
            properties["created_at"] = datetime.now().isoformat()

        # 如果传入了 knowledge_id，添加到属性
        if knowledge_id:
            properties["knowledge_id"] = knowledge_id

        query = f"""
        MERGE (n:{label} {{name: $name}})
        SET n += $properties
        """

        # 如果传入了 knowledge_id，添加引用
        if knowledge_id:
            query += f"""
            WITH n
            MERGE (n)-[:EXTRACTED_FROM]->(k {{knowledge_id: $knowledge_id}})
            """

        query += " RETURN n.name AS name"

        try:
            with self.driver.session() as session:
                result = session.run(query, name=name, properties=properties, knowledge_id=knowledge_id)
                return result.single() is not None
        except Exception as e:
            print(f"upsert_node 失败: {e}")
            return False

    def get_node(self, label: str, name: str) -> Optional[Dict[str, Any]]:
        """
        获取节点

        Args:
            label: 节点标签
            name: 节点名称

        Returns:
            节点属性字典，不存在返回 None
        """
        query = f"""
        MATCH (n:{label} {{name: $name}})
        RETURN n
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, name=name)
                record = result.single()
                if record:
                    return dict(record["n"])
                return None
        except Exception as e:
            print(f"get_node 失败: {e}")
            return None

    def delete_node(self, label: str, name: str) -> bool:
        """
        删除节点及其所有关系

        Args:
            label: 节点标签
            name: 节点名称

        Returns:
            bool: 操作是否成功
        """
        query = f"""
        MATCH (n:{label} {{name: $name}})
        DETACH DELETE n
        """

        try:
            with self.driver.session() as session:
                session.run(query, name=name)
                return True
        except Exception as e:
            print(f"delete_node 失败: {e}")
            return False

    def node_exists(self, label: str, name: str) -> bool:
        """检查节点是否存在"""
        query = f"""
        MATCH (n:{label} {{name: $name}})
        RETURN count(n) AS count
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, name=name)
                record = result.single()
                return record["count"] > 0 if record else False
        except Exception as e:
            print(f"node_exists 失败: {e}")
            return False

    # ==================== 关系操作 ====================

    def create_relation(
        self,
        from_name: str,
        from_label: str,
        to_name: str,
        to_label: str,
        rel_type: str,
        rel_properties: Dict[str, Any] = None
    ) -> bool:
        """
        创建关系

        Args:
            from_name: 起始节点名称
            from_label: 起始节点标签
            to_name: 目标节点名称
            to_label: 目标节点标签
            rel_type: 关系类型 (CONTAINS, REFERS, etc.)
            rel_properties: 关系属性

        Returns:
            bool: 操作是否成功
        """
        rel_properties = rel_properties or {}
        rel_properties["created_at"] = datetime.now().isoformat()
        rel_properties["updated_at"] = datetime.now().isoformat()

        query = f"""
        MATCH (a:{from_label} {{name: $from_name}})
        MATCH (b:{to_label} {{name: $to_name}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += $rel_properties
        RETURN r
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    from_name=from_name,
                    to_name=to_name,
                    rel_properties=rel_properties
                )
                return result.single() is not None
        except Exception as e:
            print(f"create_relation 失败: {e}")
            return False

    def delete_relation(
        self,
        from_name: str,
        to_name: str,
        rel_type: str
    ) -> bool:
        """删除关系"""
        query = f"""
        MATCH (a {{name: $from_name}})-[r:{rel_type}]->(b {{name: $to_name}})
        DELETE r
        """

        try:
            with self.driver.session() as session:
                session.run(query, from_name=from_name, to_name=to_name)
                return True
        except Exception as e:
            print(f"delete_relation 失败: {e}")
            return False

    def get_entities_by_knowledge_id(self, knowledge_id: str) -> List[Dict[str, Any]]:
        """
        获取与指定知识ID关联的所有实体

        Args:
            knowledge_id: 知识ID

        Returns:
            实体列表
        """
        query = """
        MATCH (n)-[:EXTRACTED_FROM]->(:{knowledge_id_label} {knowledge_id: $knowledge_id})
        RETURN n, labels(n)[0] AS label
        """.format(knowledge_id_label="{knowledge_id_label}")

        try:
            with self.driver.session() as session:
                result = session.run(
                    query.replace("{knowledge_id_label}", ""),
                    knowledge_id=knowledge_id
                )
                entities = []
                for record in result:
                    node = dict(record["n"])
                    node["label"] = record["label"]
                    entities.append(node)
                return entities
        except Exception as e:
            print(f"get_entities_by_knowledge_id 失败: {e}")
            return []

    def get_node_ref_count(self, label: str, name: str) -> int:
        """
        获取节点被多少个知识引用

        Args:
            label: 节点标签
            name: 节点名称

        Returns:
            引用数量
        """
        query = f"""
        MATCH (n:{label} {{name: $name}})-[:EXTRACTED_FROM]->(k)
        RETURN count(k) AS ref_count
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, name=name)
                record = result.single()
                return record["ref_count"] if record else 0
        except Exception as e:
            print(f"get_node_ref_count 失败: {e}")
            return 0

    def delete_node_and_relations(self, label: str, name: str) -> bool:
        """
        删除节点及其所有关系（不检查引用计数）

        Args:
            label: 节点标签
            name: 节点名称

        Returns:
            bool: 操作是否成功
        """
        query = f"""
        MATCH (n:{label} {{name: $name}})
        DETACH DELETE n
        """

        try:
            with self.driver.session() as session:
                session.run(query, name=name)
                return True
        except Exception as e:
            print(f"delete_node_and_relations 失败: {e}")
            return False

    def remove_knowledge_reference(self, knowledge_id: str) -> Dict[str, Any]:
        """
        移除知识引用，如果实体不再被任何知识引用则删除

        Args:
            knowledge_id: 知识ID

        Returns:
            清理结果统计
        """
        stats = {
            "entities_checked": 0,
            "entities_deleted": 0,
            "entities_retained": 0,
            "relations_deleted": 0
        }

        # 找到该知识引用的所有实体
        query = """
        MATCH (n)-[r:EXTRACTED_FROM]->(k)
        WHERE k.knowledge_id = $knowledge_id
        RETURN n, labels(n)[0] AS label
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, knowledge_id=knowledge_id)

                for record in result:
                    stats["entities_checked"] += 1
                    node = record["n"]
                    node_label = record["label"]
                    node_name = node.get("name", "")

                    if not node_name:
                        continue

                    # 删除 EXTRACTED_FROM 关系
                    delete_ref_query = f"""
                    MATCH (n:{node_label} {{name: $name}})-[r:EXTRACTED_FROM]->(k {{knowledge_id: $knowledge_id}})
                    DELETE r
                    """
                    session.run(delete_ref_query, name=node_name, knowledge_id=knowledge_id)

                    # 检查是否还有其他知识引用
                    ref_count_query = f"""
                    MATCH (n:{node_label} {{name: $name}})-[:EXTRACTED_FROM]->()
                    RETURN count(*) AS ref_count
                    """
                    ref_result = session.run(ref_count_query, name=node_name)
                    ref_record = ref_result.single()
                    ref_count = ref_record["ref_count"] if ref_record else 0

                    if ref_count == 0:
                        # 没有其他引用了，删除该实体及其所有关系
                        delete_query = f"""
                        MATCH (n:{node_label} {{name: $name}})
                        DETACH DELETE n
                        """
                        session.run(delete_query, name=node_name)
                        stats["entities_deleted"] += 1
                    else:
                        stats["entities_retained"] += 1

        except Exception as e:
            print(f"remove_knowledge_reference 失败: {e}")

        return stats

    def force_delete_knowledge_reference(self, knowledge_id: str) -> Dict[str, Any]:
        """
        强制删除知识关联的所有实体（不管是否被其他知识引用）

        Args:
            knowledge_id: 知识ID

        Returns:
            删除结果统计
        """
        stats = {
            "entities_checked": 0,
            "entities_deleted": 0,
            "relations_deleted": 0
        }

        # 找到该知识引用的所有实体
        query = """
        MATCH (n)-[r:EXTRACTED_FROM]->(k)
        WHERE k.knowledge_id = $knowledge_id
        RETURN n.name as name, labels(n)[0] AS label
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, knowledge_id=knowledge_id)
                entities = [(record["name"], record["label"]) for record in result]

                stats["entities_checked"] = len(entities)
                stats["relations_deleted"] = len(entities)

                # 删除所有 EXTRACTED_FROM 关系
                delete_rels_query = """
                MATCH (n)-[r:EXTRACTED_FROM]->(k)
                WHERE k.knowledge_id = $knowledge_id
                DELETE r
                """
                session.run(delete_rels_query, knowledge_id=knowledge_id)

                # 强制删除所有关联实体（不管是否被其他知识引用）
                deleted_names = set()
                for name, label in entities:
                    if name and name not in deleted_names:
                        delete_node_query = f"""
                        MATCH (n:{label} {{name: $name}})
                        DETACH DELETE n
                        """
                        session.run(delete_node_query, name=name)
                        deleted_names.add(name)
                        stats["entities_deleted"] += 1

        except Exception as e:
            print(f"force_delete_knowledge_reference 失败: {e}")

        return stats

    def relation_exists(
        self,
        from_name: str,
        to_name: str,
        rel_type: str
    ) -> bool:
        """检查关系是否存在"""
        query = f"""
        MATCH (a {{name: $from_name}})-[r:{rel_type}]->(b {{name: $to_name}})
        RETURN count(r) AS count
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, from_name=from_name, to_name=to_name)
                record = result.single()
                return record["count"] > 0 if record else False
        except Exception as e:
            print(f"relation_exists 失败: {e}")
            return False

    # ==================== 图谱查询 ====================

    def get_related_entities(
        self,
        entity_name: str,
        depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        获取实体关联的所有节点和关系

        Args:
            entity_name: 实体名称
            depth: 查询深度（跳数）

        Returns:
            包含 nodes 和 edges 的字典列表
        """
        query = f"""
        MATCH path = (e)-[*1..{depth}]-(related)
        WHERE e.name = $entity_name
        WITH path, relationships(path) AS rels
        UNWIND nodes(path) AS node
        WITH path, collect(DISTINCT node) AS all_nodes, rels
        UNWIND rels AS rel
        WITH path, all_nodes, rel,
             startNode(rel) AS start,
             endNode(rel) AS end
        RETURN DISTINCT
               collect(DISTINCT {{id: id(start), name: start.name, label: labels(start)[0]}}) AS source_nodes,
               collect(DISTINCT {{id: id(end), name: end.name, label: labels(end)[0]}}) AS target_nodes,
               collect(DISTINCT {{type: type(rel)}}) AS rel_types
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, entity_name=entity_name)
                records = result.data()
                return records
        except Exception as e:
            print(f"get_related_entities 失败: {e}")
            return []

    def find_paths(
        self,
        from_name: str,
        to_name: str,
        max_depth: int = 4
    ) -> List[Dict[str, Any]]:
        """
        查找两实体间的所有路径

        Args:
            from_name: 起始实体名称
            to_name: 目标实体名称
            max_depth: 最大深度

        Returns:
            路径列表
        """
        query = f"""
        MATCH path = (a {{name: $from_name}})-[*1..{max_depth}]-(b {{name: $to_name}})
        RETURN path
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    from_name=from_name,
                    to_name=to_name
                )
                paths = []
                for record in result:
                    path = record["path"]
                    nodes = []
                    edges = []
                    for i, node in enumerate(path.nodes):
                        nodes.append({
                            "id": str(node.id),
                            "name": node.get("name", ""),
                            "label": list(node.labels)[0] if node.labels else ""
                        })
                        if i > 0:
                            rel = path.relationships[i - 1]
                            edges.append({
                                "source": str(path.nodes[i - 1].id),
                                "target": str(node.id),
                                "type": type(rel).__name__
                            })
                    paths.append({"nodes": nodes, "edges": edges})
                return paths
        except Exception as e:
            print(f"find_paths 失败: {e}")
            return []

    def get_subgraph(
        self,
        entity_name: str,
        depth: int = 2
    ) -> Dict[str, Any]:
        """
        获取实体周围的子图

        Args:
            entity_name: 实体名称
            depth: 深度

        Returns:
            包含 nodes 和 edges 的字典
        """
        query = f"""
        MATCH path = (e)-[*1..{depth}]-(connected)
        WHERE e.name = $entity_name
        WITH collect(DISTINCT path) AS all_paths
        RETURN all_paths
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, entity_name=entity_name)
                record = result.single()

                if not record:
                    return {"nodes": [], "edges": []}

                all_paths = record["all_paths"]
                node_map = {}
                edge_list = []

                for path in all_paths:
                    for i, node in enumerate(path.nodes):
                        node_id = str(node.id)
                        if node_id not in node_map:
                            node_map[node_id] = {
                                "id": node_id,
                                "name": node.get("name", ""),
                                "label": list(node.labels)[0] if node.labels else ""
                            }
                        if i > 0:
                            rel = path.relationships[i - 1]
                            edge_id = str(rel.id)
                            edge_list.append({
                                "id": edge_id,
                                "source": str(path.nodes[i - 1].id),
                                "target": str(node.id),
                                "type": type(rel).__name__
                            })

                return {
                    "nodes": list(node_map.values()),
                    "edges": edge_list
                }
        except Exception as e:
            print(f"get_subgraph 失败: {e}")
            return {"nodes": [], "edges": []}

    def get_entity_by_type(
        self,
        label: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        按类型获取实体列表

        Args:
            label: 节点标签
            limit: 返回数量限制

        Returns:
            实体列表
        """
        if label == "Unknown":
            query = """
            MATCH (n)
            WHERE size(labels(n)) = 0
            RETURN n
            LIMIT $limit
            """
        else:
            query = f"""
            MATCH (n:{label})
            RETURN n
            LIMIT $limit
            """

        try:
            with self.driver.session() as session:
                result = session.run(query, limit=limit)
                return [dict(record["n"]) for record in result]
        except Exception as e:
            print(f"get_entity_by_type 失败: {e}")
            return []

    # ==================== 统计 ====================

    def get_stats(self) -> Dict[str, int]:
        """获取图谱统计信息"""
        node_query = """
        MATCH (n)
        RETURN labels(n)[0] AS label, count(*) AS count
        """

        rel_query = """
        MATCH ()-[r]-()
        RETURN type(r) AS label, count(*) AS count
        """

        try:
            with self.driver.session() as session:
                node_result = session.run(node_query)
                rel_result = session.run(rel_query)

                stats = {}
                for record in node_result:
                    stats[f"node:{record['label']}"] = record["count"]
                for record in rel_result:
                    stats[f"rel:{record['label']}"] = record["count"]

                return stats
        except Exception as e:
            print(f"get_stats 失败: {e}")
            return {}

    def clear_all(self) -> bool:
        """清空所有节点和关系（危险操作！）"""
        query = """
        MATCH (n)
        DETACH DELETE n
        """

        try:
            with self.driver.session() as session:
                session.run(query)
                return True
        except Exception as e:
            print(f"clear_all 失败: {e}")
            return False

    # ==================== 批量操作 ====================

    def batch_upsert_nodes(
        self,
        label: str,
        nodes: List[Dict[str, Any]]
    ) -> int:
        """
        批量插入或更新节点

        Args:
            label: 节点标签
            nodes: 节点列表，每个节点包含 name 和其他属性

        Returns:
            成功插入的数量
        """
        success_count = 0
        for node in nodes:
            name = node.get("name")
            if not name:
                continue
            properties = {k: v for k, v in node.items() if k != "name"}
            if self.upsert_node(label, name, properties):
                success_count += 1
        return success_count

    def batch_create_relations(
        self,
        relations: List[Dict[str, str]]
    ) -> int:
        """
        批量创建关系

        Args:
            relations: 关系列表，每个包含 from_name, from_label, to_name, to_label, rel_type

        Returns:
            成功创建的数量
        """
        success_count = 0
        for rel in relations:
            if all(k in rel for k in ["from_name", "from_label", "to_name", "to_label", "rel_type"]):
                if self.create_relation(
                    rel["from_name"],
                    rel["from_label"],
                    rel["to_name"],
                    rel["to_label"],
                    rel["rel_type"],
                    rel.get("properties")
                ):
                    success_count += 1
        return success_count

    # ==================== 图谱浏览功能 ====================

    def get_graph_stats(self) -> Dict[str, Any]:
        """获取图谱统计信息"""
        # 节点统计（排除无标签且无name的引用节点）
        node_query = """
        MATCH (n)
        WHERE size(labels(n)) > 0 OR n.name IS NOT NULL
        RETURN labels(n)[0] AS label, count(*) AS count
        ORDER BY count DESC
        """

        # 边统计
        rel_query = """
        MATCH ()-[r]-()
        RETURN type(r) AS label, count(*) AS count
        """

        # 总节点数（排除无标签且无name的引用节点）
        total_nodes_query = """
        MATCH (n)
        WHERE size(labels(n)) > 0 OR n.name IS NOT NULL
        RETURN count(n) AS total
        """

        # 总边数
        total_edges_query = "MATCH ()-[r]-() RETURN count(r) AS total"

        try:
            with self.driver.session() as session:
                node_result = session.run(node_query)
                rel_result = session.run(rel_query)
                total_nodes_result = session.run(total_nodes_query)
                total_edges_result = session.run(total_edges_query)

                by_type = {}
                for record in node_result:
                    label = record["label"] or "Unknown"
                    by_type[label] = record["count"]

                return {
                    "total_nodes": total_nodes_result.single()["total"] if total_nodes_result.peek() else 0,
                    "total_edges": total_edges_result.single()["total"] if total_edges_result.peek() else 0,
                    "by_type": by_type
                }
        except Exception as e:
            print(f"get_graph_stats 失败: {e}")
            return {"total_nodes": 0, "total_edges": 0, "by_type": {}}

    def cleanup_node_names(self) -> Dict[str, int]:
        """清理节点名称中的换行符等空白字符"""
        query = """
        MATCH (n)
        WHERE n.name CONTAINS '\n' OR n.name CONTAINS '\r' OR n.name CONTAINS '\t'
        WITH n, replace(replace(replace(n.name, '\n', ''), '\r', ''), '\t', '') AS cleaned_name
        SET n.name = cleaned_name
        RETURN count(n) AS cleaned_count
        """
        try:
            with self.driver.session() as session:
                result = session.run(query)
                record = result.single()
                return {"cleaned_count": record["cleaned_count"] if record else 0}
        except Exception as e:
            print(f"cleanup_node_names 失败: {e}")
            return {"cleaned_count": 0, "error": str(e)}

    def get_center_nodes(self, limit: int = 50) -> Dict[str, Any]:
        """
        获取中心节点（按度数排序，用于初始采样展示）

        Args:
            limit: 返回节点数量

        Returns:
            包含 nodes 和 edges 的字典
        """
        # 先获取度数最高的节点
        nodes_query = """
        MATCH (n)
        WHERE size([(n)--() | 1]) > 0
        WITH n, size([(n)--() | 1]) AS degree
        ORDER BY degree DESC
        LIMIT $limit
        RETURN n, degree
        """

        try:
            with self.driver.session() as session:
                nodes_result = session.run(nodes_query, limit=limit)

                node_map = {}
                nodes_list = []
                for record in nodes_result:
                    node = record["n"]
                    node_id = str(node.id)
                    node_data = {
                        "id": node_id,
                        "name": node.get("name", ""),
                        "label": list(node.labels)[0] if node.labels else "",
                        "degree": record["degree"],
                        "knowledge_id": node.get("knowledge_id", None)
                    }
                    nodes_list.append(node_data)
                    node_map[node_id] = node_data

                # 获取这些节点的所有边
                if not node_map:
                    return {"nodes": [], "edges": []}

                edges_query = """
                MATCH (a)-[r]-(b)
                WHERE a.name IN $node_names
                RETURN a, b, type(r) AS rel_type, id(r) AS rel_id
                """

                node_names = [n["name"] for n in nodes_list]
                edges_result = session.run(edges_query, node_names=node_names)

                edges_list = []
                for record in edges_result:
                    source_node = record["a"]
                    target_node = record["b"]
                    edges_list.append({
                        "id": str(record["rel_id"]),
                        "source": str(source_node.id),
                        "target": str(target_node.id),
                        "type": record["rel_type"]
                    })

                return {"nodes": nodes_list, "edges": edges_list}
        except Exception as e:
            print(f"get_center_nodes 失败: {e}")
            return {"nodes": [], "edges": []}

    def get_neighbors(self, node_name: str, depth: int = 1) -> Dict[str, Any]:
        """
        获取节点的邻居节点

        Args:
            node_name: 节点名称
            depth: 深度（1或2）

        Returns:
            包含 nodes 和 edges 的字典
        """
        if depth == 1:
            query = """
            MATCH (center)-[r]-(neighbor)
            WHERE center.name = $node_name
            RETURN center, r, neighbor
            """
        else:
            query = """
            MATCH path = (center)-[*1..2]-(neighbor)
            WHERE center.name = $node_name
            RETURN path
            """

        try:
            with self.driver.session() as session:
                if depth == 1:
                    result = session.run(query, node_name=node_name)
                    node_map = {}
                    edges_list = []

                    for record in result:
                        center = record["center"]
                        neighbor = record["neighbor"]
                        rel = record["r"]

                        center_id = str(center.id)
                        if center_id not in node_map:
                            node_map[center_id] = {
                                "id": center_id,
                                "name": center.get("name", ""),
                                "label": list(center.labels)[0] if center.labels else ""
                            }

                        neighbor_id = str(neighbor.id)
                        if neighbor_id not in node_map:
                            node_map[neighbor_id] = {
                                "id": neighbor_id,
                                "name": neighbor.get("name", ""),
                                "label": list(neighbor.labels)[0] if neighbor.labels else ""
                            }

                        edges_list.append({
                            "id": str(rel.id),
                            "source": center_id,
                            "target": neighbor_id,
                            "type": rel.type
                        })

                    return {"nodes": list(node_map.values()), "edges": edges_list}
                else:
                    result = session.run(query, node_name=node_name)
                    node_map = {}
                    edges_list = []

                    for record in result:
                        path = record["path"]
                        for i, node in enumerate(path.nodes):
                            node_id = str(node.id)
                            if node_id not in node_map:
                                node_map[node_id] = {
                                    "id": node_id,
                                    "name": node.get("name", ""),
                                    "label": list(node.labels)[0] if node.labels else ""
                                }
                            if i > 0:
                                rel = path.relationships[i - 1]
                                edges_list.append({
                                    "id": str(rel.id),
                                    "source": str(path.nodes[i - 1].id),
                                    "target": node_id,
                                    "type": type(rel).__name__
                                })

                    return {"nodes": list(node_map.values()), "edges": edges_list}
        except Exception as e:
            print(f"get_neighbors 失败: {e}")
            return {"nodes": [], "edges": []}

    def search_nodes(self, keyword: str = None, label: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        搜索节点

        Args:
            keyword: 搜索关键词（可选，为空时返回指定标签的节点）
            label: 可选，按类型筛选
            limit: 返回数量

        Returns:
            匹配的节点列表
        """
        if keyword and label:
            query = f"""
            MATCH (n:{label})
            WHERE n.name CONTAINS $keyword
            RETURN n, labels(n)[0] AS label
            LIMIT $limit
            """
        elif keyword:
            query = """
            MATCH (n)
            WHERE n.name CONTAINS $keyword
            RETURN n, labels(n)[0] AS label
            LIMIT $limit
            """
        elif label:
            if label == "Unknown":
                # 查找没有标签且没有name的节点（知识引用节点，不是真正的实体）
                # 排除只有knowledge_id属性的节点
                query = """
                MATCH (n)
                WHERE size(labels(n)) = 0 AND n.name IS NULL
                RETURN n, labels(n)[0] AS label
                LIMIT $limit
                """
            else:
                query = f"""
                MATCH (n:{label})
                RETURN n, labels(n)[0] AS label
                LIMIT $limit
                """
        else:
            query = """
            MATCH (n)
            RETURN n, labels(n)[0] AS label
            LIMIT $limit
            """

        try:
            with self.driver.session() as session:
                result = session.run(query, keyword=keyword, limit=limit)
                return [
                    {
                        "id": str(record["n"].id),
                        "name": record["n"].get("name", ""),
                        "label": record["label"],
                        "matched_on": "name" if keyword else None,
                        "knowledge_id": record["n"].get("knowledge_id", None)
                    }
                    for record in result
                ]
        except Exception as e:
            print(f"search_nodes 失败: {e}")
            return []

    def get_node_relations(self, node_name: str) -> List[Dict[str, Any]]:
        """
        获取节点的所有关联关系

        Args:
            node_name: 节点名称

        Returns:
            关系列表，包含类型、方向、目标/源节点
        """
        query = """
        MATCH (center)-[r]-(connected)
        WHERE center.name = $node_name AND connected.name IS NOT NULL
        RETURN center, r, connected, labels(center)[0] AS center_label, labels(connected)[0] AS connected_label,
               startNode(r) = center AS is_outgoing
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, node_name=node_name)
                relations = []
                for record in result:
                    rel = record["r"]
                    connected = record["connected"]
                    is_outgoing = record["is_outgoing"]

                    relations.append({
                        "id": str(rel.id),
                        "type": rel.type,  # 使用neo4j的关系类型
                        "direction": "outgoing" if is_outgoing else "incoming",
                        "target_name": connected.get("name", "") if is_outgoing else record["center"].get("name", ""),
                        "target_label": record["connected_label"] if is_outgoing else record["center_label"],
                        "source_name": record["center"].get("name", "") if is_outgoing else connected.get("name", ""),
                        "source_label": record["center_label"] if is_outgoing else record["connected_label"]
                    })
                return relations
        except Exception as e:
            print(f"get_node_relations 失败: {e}")
            return []


# 全局单例
_neo4j_service: Optional[Neo4jService] = None


def get_neo4j_service() -> Neo4jService:
    """获取 Neo4j 服务单例"""
    global _neo4j_service
    if _neo4j_service is None:
        _neo4j_service = Neo4jService()
    return _neo4j_service


def close_neo4j_service():
    """关闭 Neo4j 服务"""
    global _neo4j_service
    if _neo4j_service is not None:
        _neo4j_service.close()
        _neo4j_service = None
