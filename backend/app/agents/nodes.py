import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_models import ChatTongyi
from app.config import settings
from app.agents.state import AgentState
from app.tools.amap_tools import search_poi, calculate_route
from app.tools.rag_tools import search_local_hidden_gems

# 初始化通义千问大模型 (绑定工具)
llm = ChatTongyi(model=settings.llm_model_name, dashscope_api_key=settings.dashscope_api_key)
# 将 Phase 2 写的工具绑定给大模型，使其具备 Function Calling 能力
llm_with_tools = llm.bind_tools([search_poi, calculate_route, search_local_hidden_gems])


def planner_node(state: AgentState) -> dict:
    """需求分析 Agent：将自然语言转化为结构化需求"""
    prompt = """你是一个专业的旅行需求分析师。请根据用户的输入，提取结构化的旅行需求。
    必须输出严格的 JSON 格式，包含以下字段：
    - destination (目的地)
    - days (天数)
    - budget (预算，数字)
    - preferences (偏好列表，如：小众、美食、不早起)
    如果用户没有提供某项信息，请根据常识合理推断或留空。只输出 JSON，不要输出其他内容。"""

    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=state["user_input"])
    ])

    try:
        # 尝试解析 JSON
        reqs = json.loads(response.content)
    except json.JSONDecodeError:
        reqs = {"destination": "未知", "days": 3, "budget": 3000, "preferences": ["休闲"]}

    return {
        "requirements": reqs,
        "message_history": [f"Planner 提取需求: {json.dumps(reqs, ensure_ascii=False)}"]
    }


def researcher_node(state: AgentState) -> dict:
    """信息调研 Agent：调用工具获取真实数据"""
    reqs = state["requirements"]
    dest = reqs.get("destination", "杭州")
    prefs = reqs.get("preferences", [])

    # 1. 调用高德地图搜索核心景点
    poi_data = search_poi.invoke({"keywords": f"{dest} 必去景点", "city": dest})

    # 2. 如果偏好包含“小众”，调用本地 RAG 知识库
    rag_data = ""
    if any(p in prefs for p in ["小众", "避开人挤人", "小众打卡地"]):
        rag_data = search_local_hidden_gems.invoke({"query": f"{dest} 小众景点推荐"})

    combined_data = f"【高德地图热门景点数据】:\n{poi_data}\n\n【本地小众/避雷指南】:\n{rag_data}"

    return {
        "research_data": combined_data,
        "message_history": ["Researcher 完成了地图和知识库的数据调研"]
    }


def builder_node(state: AgentState) -> dict:
    """行程编排 Agent：生成详细行程"""
    prompt = f"""你是一个资深旅行定制师。请根据以下需求和调研数据，生成一份详细的 Markdown 格式旅行行程。
    要求：
    1. 包含每天的具体时间安排、景点/餐厅名称、交通方式建议。
    2. 结合“本地小众/避雷指南”中的提示，避开人流高峰或加入小众体验。
    3. 如果之前的审查意见（Feedback）不为空，请务必根据意见进行修改！

    【用户需求】: {json.dumps(state['requirements'], ensure_ascii=False)}
    【调研数据】: {state['research_data']}
    【审查意见】: {state.get('review_feedback', '无')}
    """

    response = llm.invoke([
        SystemMessage(content="你是一个严谨的旅行定制师，只输出 Markdown 格式的行程，不要说废话。"),
        HumanMessage(content=prompt)
    ])

    return {
        "draft_itinerary": response.content,
        "message_history": ["Builder 生成了新的行程草稿"]
    }


def reviewer_node(state: AgentState) -> dict:
    """反思质检 Agent：审查行程的物理合理性与需求匹配度"""
    prompt = f"""你是一个严格的行程质检员。请审查以下旅行行程是否合理。
    审查维度：
    1. 路线是否合理？（同一天安排的景点是否距离过远、时间是否来得及）
    2. 是否满足了用户的预算和偏好？
    3. 是否考虑了避雷指南中的提示？

    【用户需求】: {json.dumps(state['requirements'], ensure_ascii=False)}
    【当前行程草稿】: {state['draft_itinerary']}

    如果行程非常完美，请回复 "PASS"。
    如果有不合理之处，请明确指出问题所在，并给出具体的修改建议（不要自己重写行程，只给建议）。"""

    response = llm.invoke([
        SystemMessage(content="你是一个严格的质检员。"),
        HumanMessage(content=prompt)
    ])

    feedback = response.content
    is_valid = "PASS" in feedback.upper()

    return {
        "review_feedback": feedback if not is_valid else "",
        "is_valid": is_valid,
        "revision_count": state.get("revision_count", 0) + 1,
        "message_history": [f"Reviewer 审查结果: {'通过' if is_valid else '打回重做'}"]
    }