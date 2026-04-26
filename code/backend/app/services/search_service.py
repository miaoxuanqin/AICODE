from typing import List, Optional, Dict, Any
from elasticsearch import Elasticsearch
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.config import get_settings

settings = get_settings()


class SearchService:
    """搜索服务，封装 Elasticsearch 操作"""

    INDEX_NAME = "knowledge"

    def __init__(self):
        self.es = Elasticsearch([settings.elasticsearch_url])
        self.qdrant = QdrantClient(url=settings.qdrant_url)

    def ensure_es_index(self):
        """确保 Elasticsearch 索引存在"""
        try:
            if not self.es.indices.exists(index=self.INDEX_NAME):
                mapping = {
                    "mappings": {
                        "properties": {
                            "id": {"type": "keyword"},
                            "title": {"type": "text"},
                            "content": {"type": "text"},
                            "summary": {"type": "text"},
                            "category": {"type": "keyword"},
                            "source": {"type": "text"},
                            "tags": {"type": "keyword"},
                            "user_id": {"type": "keyword"},
                            "created_at": {"type": "date"},
                            "view_count": {"type": "integer"}
                        }
                    }
                }
                self.es.indices.create(index=self.INDEX_NAME, body=mapping)
        except Exception as e:
            print(f"ES索引创建失败: {e}")

    def _convert_date(self, created_at: str) -> str:
        """转换日期格式为ISO格式"""
        from datetime import datetime
        if isinstance(created_at, str):
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                try:
                    dt = datetime.strptime(created_at[:19], fmt)
                    return dt.isoformat()
                except ValueError:
                    continue
        return created_at

    def index_knowledge(self, knowledge_id: str, title: str, content: str,
                         summary: str, category: str, source: str, tags: List[str],
                         user_id: str, created_at: str, view_count: int = 0):
        """索引知识到 ES"""
        self.ensure_es_index()

        created_at = self._convert_date(created_at)

        doc = {
            "id": knowledge_id,
            "title": title,
            "content": content,
            "summary": summary,
            "category": category,
            "source": source,
            "tags": tags,
            "user_id": user_id,
            "created_at": created_at,
            "view_count": view_count
        }
        self.es.index(index=self.INDEX_NAME, id=knowledge_id, body=doc)

    def delete_knowledge_index(self, knowledge_id: str):
        """删除知识索引"""
        try:
            self.es.delete(index=self.INDEX_NAME, id=knowledge_id)
        except Exception:
            pass

    def get_by_id(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取知识文档"""
        try:
            result = self.es.get(index=self.INDEX_NAME, id=knowledge_id)
            return result["_source"]
        except Exception:
            return None

    def search_keyword(self, query: str, user_id: str, category: Optional[str] = None,
                       page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """关键词搜索（ES）"""
        self.ensure_es_index()

        must_conditions = [
            {"term": {"user_id": user_id}},
            {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "content", "summary^2"],
                    "type": "best_fields"
                }
            }
        ]

        if category:
            must_conditions.append({"term": {"category": category}})

        body = {
            "query": {
                "bool": {
                    "must": must_conditions
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {"fragment_size": 150, "number_of_fragments": 3},
                    "summary": {}
                }
            },
            "from": (page - 1) * page_size,
            "size": page_size,
            "sort": [
                {"_score": "desc"},
                {"created_at": "desc"}
            ]
        }

        result = self.es.search(index=self.INDEX_NAME, body=body)

        hits = result["hits"]["hits"]
        total = result["hits"]["total"]["value"]

        items = []
        for hit in hits:
            item = {
                "id": hit["_source"]["id"],
                "title": hit["_source"]["title"],
                "summary": hit["_source"]["summary"],
                "category": hit["_source"]["category"],
                "source": hit["_source"].get("source", ""),
                "tags": hit["_source"].get("tags", []),
                "view_count": hit["_source"].get("view_count", 0),
                "score": hit["_score"],
                "highlight": hit.get("highlight", {})
            }
            items.append(item)

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def search_hybrid(self, query: str, user_id: str, category: Optional[str] = None,
                      page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """混合搜索：暂定直接走关键词搜索"""
        return self.search_keyword(query, user_id, category, page, page_size)

    def search_vector(self, query_vector: List[float], user_id: str,
                     category: Optional[str] = None, limit: int = 5) -> List[str]:
        """向量搜索（Qdrant），返回知识ID列表"""
        collection_name = "knowledge"

        try:
            # 构建过滤条件
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            # Qdrant 中 user_id 存储为字符串，直接使用
            must_conditions = [FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            if category:
                must_conditions.append(FieldCondition(key="category", match=MatchValue(value=category)))

            search_filter = Filter(must=must_conditions)

            results = self.qdrant.query_points(
                collection_name=collection_name,
                query=query_vector,
                query_filter=search_filter,
                limit=limit
            )

            return [hit.id for hit in results.points]

        except Exception as e:
            print(f"向量搜索失败: {e}")
            return []

    def index_vector(self, knowledge_id: str, title: str, content: str,
                     category: str, user_id: str):
        """将知识向量存储到 Qdrant"""
        from app.services.embedding_service import embedding_service

        collection_name = "knowledge"
        vector_size = 768  # text2vec-base-chinese 向量维度

        try:
            # 确保 collection 存在
            collections = self.qdrant.get_collections().collections
            if not any(c.name == collection_name for c in collections):
                self.qdrant.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )

            # 生成向量
            text = f"{title} {content[:1000]}"  # 截取前1000字
            vector = embedding_service.encode_single(text)

            # 存储向量
            point = PointStruct(
                id=knowledge_id,
                vector=vector,
                payload={
                    "title": title,
                    "content": content[:500],
                    "category": category,
                    "user_id": user_id
                }
            )

            self.qdrant.upsert(collection_name=collection_name, points=[point])

        except Exception as e:
            print(f"向量索引失败: {e}")

    def get_hot_knowledge(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门知识"""
        self.ensure_es_index()

        body = {
            "query": {
                "term": {"user_id": user_id}
            },
            "sort": [{"view_count": "desc"}],
            "size": limit
        }

        result = self.es.search(index=self.INDEX_NAME, body=body)
        return [
            {
                "id": hit["_source"]["id"],
                "title": hit["_source"]["title"],
                "view_count": hit["_source"].get("view_count", 0),
                "category": hit["_source"]["category"]
            }
            for hit in result["hits"]["hits"]
        ]

    def get_latest_knowledge(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最新知识"""
        self.ensure_es_index()

        body = {
            "query": {
                "term": {"user_id": user_id}
            },
            "sort": [{"created_at": "desc"}],
            "size": limit
        }

        result = self.es.search(index=self.INDEX_NAME, body=body)
        return [
            {
                "id": hit["_source"]["id"],
                "title": hit["_source"]["title"],
                "created_at": hit["_source"]["created_at"],
                "category": hit["_source"]["category"]
            }
            for hit in result["hits"]["hits"]
        ]

    def suggest(self, query: str, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索建议/自动补全"""
        self.ensure_es_index()

        body = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"user_id": user_id}},
                        {
                            "match_phrase_prefix": {
                                "title": {
                                    "query": query,
                                    "max_expansions": 10
                                }
                            }
                        }
                    ]
                }
            },
            "size": limit,
            "_source": ["title"]
        }

        result = self.es.search(index=self.INDEX_NAME, body=body)
        return [{"text": hit["_source"]["title"]} for hit in result["hits"]["hits"]]


search_service = SearchService()