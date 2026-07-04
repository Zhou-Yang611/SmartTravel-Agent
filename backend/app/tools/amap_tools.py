import httpx
from langchain_core.tools import tool
from app.config import settings


@tool
def search_poi(keywords: str, city: str) -> str:
    """
    根据关键词和城市搜索景点、餐厅等 POI (Point of Interest) 信息。
    返回包含名称、地址、经纬度、评分等信息的列表。
    当用户询问某个地方有什么好玩的、好吃的，或者需要获取具体地点的经纬度时使用此工具。
    """
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "key": settings.amap_api_key,
        "keywords": keywords,
        "city": city,
        "output": "json",
        "offset": 5,  # 限制返回数量，避免上下文 Token 爆炸
        "page": 1
    }

    # 使用 httpx 发送同步请求 (在 Tool 中保持简单稳定)
    with httpx.Client() as client:
        response = client.get(url, params=params)
        data = response.json()

    if data.get("status") != "1":
        return f"API 调用失败: {data.get('info', '未知错误')}"

    pois = data.get("pois", [])
    if not pois:
        return "未找到相关地点。"

    result = []
    for poi in pois:
        result.append({
            "name": poi.get("name"),
            "address": poi.get("address"),
            "location": poi.get("location"),  # "经度,纬度" 格式
            "type": poi.get("type"),
            "biz_ext": poi.get("biz_ext", {})  # 包含评分、消费等扩展信息
        })
    return str(result)


@tool
def calculate_route(origin: str, destination: str) -> str:
    """
    计算两个地点之间的路线距离和预计时间。
    参数 origin 和 destination 必须是 "经度,纬度" 格式 (例如 "116.481028,39.989643")。
    当需要评估两个景点之间的通勤成本、判断行程顺序是否合理时使用此工具。
    """
    url = "https://restapi.amap.com/v3/direction/driving"  # 使用驾车路线作为通用距离参考
    params = {
        "key": settings.amap_api_key,
        "origin": origin,
        "destination": destination,
        "output": "json"
    }

    with httpx.Client() as client:
        response = client.get(url, params=params)
        data = response.json()

    if data.get("status") != "1":
        return f"API 调用失败: {data.get('info', '未知错误')}"

    route = data.get("route", {})
    paths = route.get("paths", [])
    if not paths:
        return "未找到可行路线。"

    best_path = paths[0]
    distance = best_path.get("distance")  # 米
    duration = best_path.get("duration")  # 秒

    return f"距离: {distance}米, 预计驾车时间: {duration}秒 (约 {int(duration) // 60} 分钟)。"