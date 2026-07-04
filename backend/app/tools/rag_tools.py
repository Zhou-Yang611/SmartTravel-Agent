import chromadb
from langchain_core.tools import tool
from langchain_community.embeddings import DashScopeEmbeddings
from app.config import settings

# 在模块级别初始化客户端和模型，避免每次调用工具都重新加载（提升性能）
_client = chromadb.PersistentClient(path=settings.vector_db_path)
_embeddings = DashScopeEmbeddings(
    model=settings.embedding_model_name,
    dashscope_api_key=settings.dashscope_api_key
)


@tool
def search_local_hidden_gems(query: str) -> str:
    """
    搜索本地的小众景点、特色美食或避雷指南。
    当用户要求“避开人挤人”、“寻找小众打卡地”、“本地人推荐的美食”或需要了解某个景点的真实评价和游玩提示时，使用此工具。
    """
    try:
        collection = _client.get_collection(name=settings.collection_name)
    except Exception:
        return "本地知识库尚未初始化或不存在，请提示管理员运行 init_vector_db.py 脚本。"

    # 将用户的查询文本向量化
    query_embedding = _embeddings.embed_query(query)

    # 在 ChromaDB 中检索最相似的 3 条记录
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "metadatas"]
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return "未在本地知识库中找到相关的小众推荐。"

    output = []
    for doc, meta in zip(documents, metadatas):
        output.append(f"地点: {meta.get('name')} ({meta.get('category')})\n"
                      f"标签: {meta.get('tags')}\n"
                      f"详细信息与提示: {doc}\n")

    return "\n---\n".join(output)