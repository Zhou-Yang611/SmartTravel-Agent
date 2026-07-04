from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import AgentState
from app.agents.nodes import planner_node, researcher_node, builder_node, reviewer_node


def should_revise(state: AgentState) -> str:
    """条件边路由函数：决定是结束还是让 Builder 重新生成"""
    # 如果审查通过，或者修改次数达到上限（防止死循环），则结束
    if state["is_valid"] or state.get("revision_count", 0) >= 3:
        return "end"
    # 否则，打回给 Builder 节点重新生成
    return "builder"


def build_graph():
    """构建 Multi-Agent 协作图"""
    workflow = StateGraph(AgentState)

    # 1. 添加节点
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("builder", builder_node)
    workflow.add_node("reviewer", reviewer_node)

    # 2. 添加边 (流转逻辑)
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "builder")
    workflow.add_edge("builder", "reviewer")

    # 3. 添加条件边 (Reviewer 之后的循环逻辑)
    workflow.add_conditional_edges(
        "reviewer",
        should_revise,
        {
            "builder": "builder",  # 如果返回 "builder"，则流转回 builder 节点
            "end": END  # 如果返回 "end"，则结束整个流程
        }
    )

    # 编译图
    return workflow.compile(checkpointer=MemorySaver())


# 导出编译好的 Agent 应用
travel_agent_app = build_graph()