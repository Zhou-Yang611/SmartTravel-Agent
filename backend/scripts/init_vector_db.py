import json
import os
import sys
import chromadb
from chromadb.errors import NotFoundError
from langchain_community.embeddings import DashScopeEmbeddings

# 将 app 目录加入 sys.path 以便导入 config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import settings


def init_vector_store():
    print("🚀 开始初始化本地小众景点向量库...")

    # 1. 加载模拟数据
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'local_pois.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        pois = json.load(f)

    documents = []
    metadatas = []
    ids = []

    for poi in pois:
        # 将核心信息拼接成一段文本，用于 Embedding
        doc_text = f"名称: {poi['name']}, 类别: {poi['category']}, 城市: {poi['city']}. " \
                   f"描述: {poi['description']}. 游玩提示: {poi['tips']}"

        documents.append(doc_text)
        metadatas.append({
            "name": poi['name'],
            "category": poi['category'],
            "city": poi['city'],
            "tags": ",".join(poi['tags'])
        })
        ids.append(poi['id'])

    print(f"✅ 成功加载 {len(documents)} 条 POI 数据。")

    # 2. 初始化 Embedding 模型 (使用通义千问的 text-embedding-v2)
    print("⏳ 正在初始化 DashScope Embedding 模型...")
    embeddings = DashScopeEmbeddings(
        model=settings.embedding_model_name,
        dashscope_api_key=settings.dashscope_api_key
    )

    # 3. 初始化 ChromaDB 客户端 (持久化到本地目录)
    client = chromadb.PersistentClient(path=settings.vector_db_path)

    # 如果 collection 已存在则删除，确保每次运行都是最新数据
    try:
        client.delete_collection(settings.collection_name)
    except (ValueError, NotFoundError):
        pass

    collection = client.create_collection(
        name=settings.collection_name,
        metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
    )

    # 4. 生成向量并写入数据库
    print("⏳ 正在生成向量并写入 ChromaDB (这可能需要几秒钟)...")
    # 注意：如果数据量大，这里应该分批 (batch) 处理
    vector_embeddings = embeddings.embed_documents(documents)

    collection.add(
        embeddings=vector_embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"🎉 向量库初始化完成！数据已持久化至: {settings.vector_db_path}")
    print(f"📊 Collection '{settings.collection_name}' 当前包含 {collection.count()} 条数据。")


if __name__ == "__main__":
    init_vector_store()