import json
import asyncio
import traceback
from app.agents.graph import travel_agent_app


# 🌟 修改函数签名，增加 session_id
async def generate_stream(user_input: str, session_id: str = "default_session"):
    """将 LangGraph 的执行过程转化为 SSE 流 (增加容错与多轮会话支持)"""
    initial_state = {
        "user_input": user_input,
        "requirements": {},
        "research_data": "",
        "draft_itinerary": "",
        "review_feedback": "",
        "is_valid": False,
        "revision_count": 0,
        "message_history": []
    }

    # 🌟 核心修复：构建 config，传入 thread_id 给 Checkpointer
    config = {"configurable": {"thread_id": session_id}}

    try:
        # 🌟 核心修复：在调用大模型前，立刻 yield 第一个状态，打破前端的 60s 超时计时器
        yield format_sse({"type": "status", "content": "🚀 智游 Agent 已唤醒，正在连接大模型..."})
        # 🌟 在 astream 中传入 config
        async for event in travel_agent_app.astream(initial_state, config=config, stream_mode="updates"):
            for node_name, node_output in event.items():

                # ... (中间的节点判断和 yield 代码保持不变) ...
                if node_name == "planner":
                    yield format_sse({"type": "status", "content": "🤖 正在分析您的旅行需求..."})
                elif node_name == "researcher":
                    yield format_sse({"type": "status", "content": "🗺️ 正在搜索地图与小众攻略..."})
                elif node_name == "builder":
                    yield format_sse({"type": "status", "content": "📝 正在为您编排详细行程..."})
                elif node_name == "reviewer":
                    is_valid = node_output.get("is_valid", False)
                    if not is_valid:
                        feedback = node_output.get("review_feedback", "")
                        yield format_sse({"type": "review",
                                          "content": f"🔍 质检员发现问题，正在重新规划...\n核心建议: {feedback[:100]}..."})
                        yield format_sse({"type": "status", "content": "🔄 正在根据建议修改行程..."})
                    else:
                        yield format_sse({"type": "status", "content": "✅ 行程质检通过，正在输出最终结果..."})

                if node_name == "builder" and "draft_itinerary" in node_output:
                    itinerary = node_output["draft_itinerary"]
                    chunk_size = 10
                    for i in range(0, len(itinerary), chunk_size):
                        chunk = itinerary[i:i + chunk_size]
                        yield format_sse({"type": "itinerary_chunk", "content": chunk})
                        await asyncio.sleep(0.02)

                if node_name == "reviewer" and node_output.get("is_valid"):
                    yield format_sse({"type": "done", "content": "行程生成完毕！"})

    except Exception as e:
        error_msg = f"系统内部错误: {str(e)}"
        print(f"❌ Agent 运行出错: {error_msg}")
        traceback.print_exc()
        yield format_sse({"type": "error", "content": error_msg})

    finally:
        yield format_sse({"type": "done", "content": "连接关闭"})


def format_sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"