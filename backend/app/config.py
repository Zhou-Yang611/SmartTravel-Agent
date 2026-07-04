import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# 加载 .env 文件
load_dotenv()


class Settings(BaseSettings):
    # 阿里云配置
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY", "")
    amap_api_key: str = os.getenv("AMAP_API_KEY", "")

    # 模型配置
    llm_model_name: str = os.getenv("LLM_MODEL_NAME", "qwen-max")
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-v2")

    # 向量库配置
    vector_db_path: str = "./vector_store"
    collection_name: str = "local_pois"

    # Pydantic V2 的配置方式
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()