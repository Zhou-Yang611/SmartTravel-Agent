import httpx
import json


def test_sse_api():
    url = "http://127.0.0.1:8000/api/chat/stream"
    payload = {"user_input": "周末去杭州玩2天，预算2000，想去小众地方吃美食"}

    print("🚀 开始请求流式 API...\n")

    # 增加 read timeout，因为多智能体反思可能需要较长时间
    timeout = httpx.Timeout(connect=10.0, read=300.0, write=10.0, pool=10.0)

    with httpx.Client(timeout=timeout) as client:
        try:
            with client.stream("POST", url, json=payload) as response:
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        json_str = line.replace("data: ", "")
                        try:
                            data = json.loads(json_str)
                            msg_type = data.get("type")
                            content = data.get("content")

                            if msg_type == "status":
                                print(f"[状态] {content}")
                            elif msg_type == "review":
                                print(f"[审查] {content}")
                            elif msg_type == "itinerary_chunk":
                                print(content, end="", flush=True)
                            elif msg_type == "error":
                                print(f"\n\n[❌ 错误] {content}")
                            elif msg_type == "done":
                                print(f"\n\n[完成] {content}")
                        except json.JSONDecodeError:
                            pass
        except httpx.RemoteProtocolError as e:
            print(f"\n\n[⚠️ 连接异常断开] {e}")
            print("请检查 uvicorn 服务端的终端日志，查看具体的 Python 报错信息！")


if __name__ == "__main__":
    test_sse_api()