"""
Embedding 服务 - 支持本地 WSL 服务和 MiniMax API
"""
import httpx
import json
from typing import List
from app.config import get_settings

settings = get_settings()


class EmbeddingService:
    """
    Embedding 服务

    支持两种模式:
    - local: WSL 本地部署的轻量模型 (text2vec-base-chinese)
    - minimax: MiniMax 云端 API
    """

    # MiniMax API
    MINIMAX_URL = "https://api.minimax.chat/v1/embeddings"
    MODEL_MINIMAX = "embo-01"

    # 本地 WSL 服务
    LOCAL_URL = "http://172.20.36.91:8001"

    def __init__(self, mode: str = None):
        """
        Args:
            mode: "local" 或 "minimax"，None 时自动检测
        """
        self.mode = mode or getattr(settings, 'embedding_mode', 'minimax')
        self.client = httpx.Client(timeout=60.0)

    def _use_local(self) -> bool:
        """是否使用本地服务"""
        return self.mode == "local"

    def embed(self, text: str, emb_type: str = "db") -> List[float]:
        """将文本转为向量"""
        if self._use_local():
            return self._embed_local([text])[0]
        return self._embed_minimax([text], emb_type)[0]

    def embed_query(self, query: str) -> List[float]:
        """将查询文本转为向量"""
        if self._use_local():
            return self._embed_local([query])[0]
        return self._embed_minimax([query], "query")[0]

    def encode_single(self, text: str) -> List[float]:
        """单个文本转为向量（embed_query 的别名）"""
        return self.embed_query(text)

    def embed_batch(self, texts: List[str], emb_type: str = "db") -> List[List[float]]:
        """批量将文本转为向量"""
        if self._use_local():
            return self._embed_local(texts)
        return self._embed_minimax(texts, emb_type)

    def _embed_local(self, texts: List[str]) -> List[List[float]]:
        """调用本地 WSL embedding 服务"""
        try:
            resp = self.client.post(
                f"{self.LOCAL_URL}/embed",
                json=texts
            )
            resp.raise_for_status()
            return resp.json()["embeddings"]
        except Exception as e:
            print(f"本地 Embedding 服务调用失败: {e}")
            raise

    def _embed_minimax(self, texts: List[str], emb_type: str) -> List[List[float]]:
        """调用 MiniMax Embedding API"""
        headers = {
            "Authorization": f"Bearer {settings.minimax_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "texts": texts,
            "model": self.MODEL_MINIMAX,
            "type": emb_type
        }

        url = f"{self.MINIMAX_URL}?GroupId={settings.minimax_group_id}"
        response = self.client.post(
            url,
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()

        data = response.json()
        return data["vectors"]

    def is_available(self) -> bool:
        """检查服务是否可用"""
        if self._use_local():
            try:
                resp = self.client.get(f"{self.LOCAL_URL}/health", timeout=5)
                return resp.status_code == 200
            except:
                return False
        return True


embedding_service = EmbeddingService()
