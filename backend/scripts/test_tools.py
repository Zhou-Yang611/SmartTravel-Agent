import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.tools.amap_tools import search_poi, calculate_route
from app.tools.rag_tools import search_local_hidden_gems

def test_all_tools():
    print("="*30)
    print("🧪 测试 1: 搜索 POI (高德地图)")
    # 使用 .invoke() 传入字典参数来调用 LangChain Tool
    poi_result = search_poi.invoke({"keywords": "西湖", "city": "杭州"})
    print(poi_result[:200] + "...\n" if len(poi_result) > 200 else poi_result)

    print("="*30)
    print("🧪 测试 2: 路线规划 (高德地图)")
    # 假设两个杭州景点的经纬度
    route_result = calculate_route.invoke({
        "origin": "120.148732,30.242425", # 西湖附近
        "destination": "120.023456,30.278912" # 良渚附近
    })
    print(route_result)

    print("="*30)
    print("🧪 测试 3: 本地小众景点检索 (RAG)")
    rag_result = search_local_hidden_gems.invoke({"query": "我想去人少一点、适合拍照的地方"})
    print(rag_result)
    print("="*30)

if __name__ == "__main__":
    test_all_tools()