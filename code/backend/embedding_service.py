"""
Embedding 服务 - 部署在 WSL 上
轻量中文 embedding 模型 (text2vec-base-chinese)
"""
from fastapi import FastAPI
from typing import List
import uvicorn

app = FastAPI(title="Embedding Service")


@app.post("/embed")
def embed(texts: List[str]):
    """
    将文本列表转为向量列表
    """
    embeddings = embedding_model.encode(texts)
    return {"embeddings": embeddings.tolist()}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # 懒加载模型，避免启动慢
    from sentence_transformers import SentenceTransformer
    print("Loading embedding model...")
    embedding_model = SentenceTransformer('shibing624/text2vec-base-chinese')
    print("Model loaded!")
    uvicorn.run(app, host="0.0.0.0", port=8001)