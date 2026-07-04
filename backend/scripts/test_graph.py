import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.graph import travel_agent_app


def test_agent_workflow():
    print("🚀 启动 SmartTravel Multi-Agent 工作流...")

    # 模拟用户输入
    user_query = "我周末想去杭州玩2天，预算2000元，不想去人挤人的地方，想吃点地道的。"

    # 初始状态
    initial_state = {
        "user_input": user_query,
        "requirements": {},
        "research_data": "",
        "draft_itinerary": "",
        "review_feedback": "",
        "is_valid": False,
        "revision_count": 0,
        "message_history": []
    }

    # 执行图 (stream_mode="values" 可以打印出每个节点执行后的状态)
    print(f"👤 用户需求: {user_query}\n")

    for event in travel_agent_app.stream(initial_state, stream_mode="updates"):
        # event 是一个字典，key 是节点名，value 是该节点返回的状态更新
        for node_name, node_output in event.items():
            print(f"--- 🤖 [{node_name.upper()}] 节点执行完毕 ---")
            if "message_history" in node_output and node_output["message_history"]:
                print(f"📝 日志: {node_output['message_history'][-1]}")
            if node_name == "builder" and "draft_itinerary" in node_output:
                print(f"📅 行程草稿预览:\n{node_output['draft_itinerary'][:200]}...\n")
            if node_name == "reviewer":
                print(f"✅ 审查是否通过: {node_output.get('is_valid')}")
                if not node_output.get('is_valid'):
                    print(f"💡 修改建议: {node_output.get('review_feedback')}\n")

    print("\n🎉 工作流执行结束！")


if __name__ == "__main__":
    test_agent_workflow()