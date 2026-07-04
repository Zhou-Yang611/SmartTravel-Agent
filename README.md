# ✈️ 智游 Agent (SmartTravel) - Multi-Agent 自动化旅行规划系统

<p align="center">
  <b>基于 LangGraph + 通义千问 + RAG 的端到端 AI 落地项目</b>
</p>

<p align="center">
  <img src="assets/demo.gif" width="300" alt="Demo GIF" />
  <img src="assets/qrcode.png" width="200" alt="体验版二维码" />
</p>
<p align="center"><i>左侧：真机流式演示 | 右侧：微信扫描体验（需添加体验成员）</i></p>

## 🌟 项目简介
针对传统旅游攻略同质化、规划耗时且缺乏实时数据的问题，独立设计并开发了一款基于多智能体协作（Multi-Agent）的自动化旅行规划系统。支持多轮对话、实时地图数据检索、RAG 本地知识库与行程动态反思调整，并通过微信小程序提供丝滑的 SSE 流式交互体验。

## 🏗️ 核心架构 (Multi-Agent Workflow)
本项目摒弃了单次 Prompt 调用，采用 **LangGraph** 构建了包含 4 个专职 Agent 的有向图（Graph），并引入了 **Reflection（反思）机制**：

1. **Planner Agent**: 将自然语言转化为结构化需求 (JSON)。
2. **Researcher Agent**: 通过 Function Calling 调用高德 API (POI/路线规划) 与本地 ChromaDB 向量库收集真实数据，消除大模型幻觉。
3. **Builder Agent**: 结合调研数据生成 Markdown 格式的详细行程。
4. **Reviewer Agent (核心亮点)**: 审查行程的物理合理性 (如距离/时间/预算冲突)。若不合理，触发**反思循环**打回给 Builder 重做，直至通过或达到最大迭代次数。

## 🛠️ 技术栈
- **后端 / AI 编排**：Python, FastAPI, LangGraph, LangChain, 通义千问 (Qwen-Max)
- **数据 / 检索**：ChromaDB (向量数据库), 高德地图 Web 服务 API
- **前端 / 客户端**：微信小程序原生开发 (WXML/WXSS/JS)

## 🚀 核心工程亮点与难点攻克

### 1. 小程序 SSE 流式渲染与粘包处理
微信小程序原生 `wx.request` 不支持 SSE。本项目基于 `enableChunked` 属性开启分块传输，并在 `onChunkReceived` 中手动处理 `ArrayBuffer`。
- **中文解码**：使用 `TextDecoder('utf-8')` 解决底层字节流中文乱码问题。
- **粘包/半包处理**：在客户端维护 `buffer` 缓冲区，按 SSE 标准的 `\n\n` 进行 split 切割，将不完整数据保留至下次拼接，彻底解决 JSON 截断导致的解析崩溃。

### 2. 工具调用容错与反思防死循环
- 为 Tool 调用增加了 Pydantic 参数校验与异常捕获，当 API 报错时，Agent 能自动解析错误信息并重试。
- 在 LangGraph 的条件边（Conditional Edges）设置 `Max Iterations = 3`，防止 Reviewer 陷入无限打回死循环，保障生产环境的稳定性与 Token 成本控制。

### 3. 多轮会话状态管理
引入 `MemorySaver` 作为 Checkpointer，通过 `thread_id` 实现全局 State 持久化，支持用户在生成行程后通过自然语言进行局部微调。

## 🏃 本地运行指南

### 后端 (Python)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# 配置 .env 文件 (填入 DASHSCOPE_API_KEY 和 AMAP_API_KEY)
python scripts/init_vector_db.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端 (微信小程序)
下载并打开 微信开发者工具。
导入 frontend 目录，AppID 选择测试号。
在“详情”->“本地设置”中，勾选 “不校验合法域名”。
编译并运行，即可在模拟器或真机预览中体验。
