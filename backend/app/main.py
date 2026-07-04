# 🌟 1. 在最顶部添加警告屏蔽 (必须在所有 import 之前)
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest
from app.services.stream_service import generate_stream

app = FastAPI(title="SmartTravel Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    流式对话接口，返回 SSE (Server-Sent Events) 格式数据
    """
    return StreamingResponse(
        # 🌟 2. 将 request.session_id 传递给 generate_stream
        generate_stream(request.user_input, request.session_id),
        media_type="text/event-stream"
    )

@app.get("/")
def read_root():
    return {"message": "SmartTravel Agent API is running!"}