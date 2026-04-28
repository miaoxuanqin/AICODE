import uuid
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
        """删除知识索引（ES + Qdrant）"""
        # 删除 ES 文档
        try:
            self.es.delete(index=self.INDEX_NAME, id=knowledge_id)
        except Exception:
            pass

        # 删除 Qdrant 向量（根据 knowledge_id 删除所有 chunks）
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            self.qdrant.delete(
                collection_name="knowledge",
                points_selector=Filter(
                    must=[FieldCondition(key="knowledge_id", match=MatchValue(value=knowledge_id))]
                )
            )
        except Exception as e:
            print(f"Qdrant 向量删除失败: {e}")

    def get_by_id(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取知识文档"""
        try:
            result = self.es.get(index=self.INDEX_NAME, id=knowledge_id)
            return result["_source"]
        except Exception:
            return None

    def search_keyword(self, query: str, user_id: str, category: Optional[str] = None,
                       page: int = 1, page_size: int = 20, is_admin: bool = False) -> Dict[str, Any]:
        """关键词搜索（ES）"""
        self.ensure_es_index()

        must_conditions = []
        if not is_admin:
            must_conditions.append({"term": {"user_id": user_id}})

        must_conditions.append({
            "multi_match": {
                "query": query,
                "fields": ["title^3", "content", "summary^2"],
                "type": "best_fields"
            }
        })

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
                      page: int = 1, page_size: int = 20, is_admin: bool = False) -> Dict[str, Any]:
        """混合搜索：暂定直接走关键词搜索"""
        return self.search_keyword(query, user_id, category, page, page_size, is_admin)

    def search_vector(self, query_vector: List[float], user_id: str,
                     category: Optional[str] = None, limit: int = 5, is_admin: bool = False) -> List[str]:
        """向量搜索（Qdrant），返回去重后的知识ID列表"""
        collection_name = "knowledge"

        try:
            # 构建过滤条件
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            must_conditions = []
            if not is_admin:
                must_conditions.append(FieldCondition(key="user_id", match=MatchValue(value=user_id)))
            if category:
                must_conditions.append(FieldCondition(key="category", match=MatchValue(value=category)))

            if must_conditions:
                search_filter = Filter(must=must_conditions)
            else:
                search_filter = None

            # 扩大搜索范围，因为每个知识现在有多个 chunk
            search_limit = limit * 3

            results = self.qdrant.query_points(
                collection_name=collection_name,
                query=query_vector,
                query_filter=search_filter,
                limit=search_limit
            )

            # 按 knowledge_id 去重，保留相关性最高的 chunk
            knowledge_ids = []
            seen = set()
            for hit in results.points:
                kid = hit.payload.get("knowledge_id") or hit.id
                if kid not in seen:
                    seen.add(kid)
                    knowledge_ids.append(kid)
                    if len(knowledge_ids) >= limit:
                        break

            return knowledge_ids

        except Exception as e:
            print(f"向量搜索失败: {e}")
            return []

    def index_vector(self, knowledge_id: str, title: str, content: str,
                     category: str, user_id: str):
        """将知识向量存储到 Qdrant（支持分片）"""
        from app.services.embedding_service import embedding_service

        collection_name = "knowledge"
        vector_size = 768  # text2vec-base-chinese 向量维度
        chunk_size = 500   # 每个 chunk 的字符数
        chunk_overlap = 50 # chunk 重叠字符数，保持上下文连贯

        try:
            # 确保 collection 存在
            collections = self.qdrant.get_collections().collections
            if not any(c.name == collection_name for c in collections):
                self.qdrant.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )

            # 文本分片
            chunks = self._split_into_chunks(content, chunk_size, chunk_overlap)

            if not chunks:
                # 内容为空，只用标题生成一个向量
                text = title
                vector = embedding_service.encode_single(text)
                point = PointStruct(
                    id=knowledge_id,
                    vector=vector,
                    payload={
                        "title": title,
                        "content": "",
                        "category": category,
                        "user_id": str(user_id),  # 统一转成字符串
                        "chunk_index": 0,
                        "total_chunks": 1,
                        "knowledge_id": knowledge_id
                    }
                )
                self.qdrant.upsert(collection_name=collection_name, points=[point])
                return

            # 批量生成向量
            texts_with_index = []
            for i, chunk in enumerate(chunks):
                # 每个 chunk 带上标题和位置信息，提升检索相关性
                texts_with_index.append(f"{title} 第{i+1}段: {chunk}")

            # 批量向量化
            vectors = embedding_service.embed_batch(texts_with_index)

            # 构建 points
            points = []
            for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
                # 生成唯一 UUID 作为 point ID（Qdrant 只接受 UUID 或 unsigned integer）
                chunk_id = str(uuid.uuid4())
                point = PointStruct(
                    id=chunk_id,
                    vector=vector,
                    payload={
                        "title": title,
                        "content": chunk,
                        "category": category,
                        "user_id": str(user_id),  # 统一转成字符串
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "knowledge_id": knowledge_id
                    }
                )
                points.append(point)

            # 批量存储
            self.qdrant.upsert(collection_name=collection_name, points=points)

        except Exception as e:
            print(f"向量索引失败: {e}")

    def _split_into_chunks(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """将文本分割成重叠的 chunks"""
        if not text:
            return []

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]

            # 去除换行符过多的碎片，保持阅读连贯性
            chunk = '\n'.join([line.strip() for line in chunk.split('\n') if line.strip()])

            if chunk:  # 只添加非空 chunk
                chunks.append(chunk)

            start += chunk_size - overlap  # 移动窗口，减去重叠部分

            # 防止无限循环
            if overlap >= chunk_size:
                break

        return chunks

    def get_hot_knowledge(self, user_id: str, limit: int = 10, is_admin: bool = False) -> List[Dict[str, Any]]:
        """获取热门知识"""
        self.ensure_es_index()

        if is_admin:
            body = {
                "query": {"match_all": {}},
                "sort": [{"view_count": "desc"}],
                "size": limit
            }
        else:
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

    def get_latest_knowledge(self, user_id: str, limit: int = 10, is_admin: bool = False) -> List[Dict[str, Any]]:
        """获取最新知识"""
        self.ensure_es_index()

        if is_admin:
            body = {
                "query": {"match_all": {}},
                "sort": [{"created_at": "desc"}],
                "size": limit
            }
        else:
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

    def suggest(self, query: str, user_id: str, limit: int = 10, is_admin: bool = False) -> List[Dict[str, Any]]:
        """搜索建议/自动补全"""
        self.ensure_es_index()

        if is_admin:
            body = {
                "query": {
                    "bool": {
                        "must": [
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
        else:
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