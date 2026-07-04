from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_input: str
    session_id: str = "default_session" # 预留字段，后续可做多轮对话记忆