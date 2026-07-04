import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage

load_dotenv()
llm = ChatTongyi(model="qwen-max", dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"))

print("正在测试通义千问 API...")
try:
    response = llm.invoke([HumanMessage(content="你好，请用一句话介绍杭州")])
    print("✅ API 调用成功:", response.content)
except Exception as e:
    print("❌ API 调用失败:", e)
