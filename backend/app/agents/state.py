from typing import TypedDict, Annotated, List
import operator


class AgentState(TypedDict):
    """多智能体协作的全局状态"""
    user_input: str  # 用户的原始输入
    requirements: dict  # Planner 提取的结构化需求
    research_data: str  # Researcher 收集的地图和 RAG 数据
    draft_itinerary: str  # Builder 生成的行程草稿
    review_feedback: str  # Reviewer 的审查意见
    is_valid: bool  # 行程是否通过审查
    revision_count: int  # 当前修改循环次数

    # 使用 operator.add 可以让列表类型的状态在节点间自动追加，而不是覆盖
    message_history: Annotated[List[str], operator.add] 