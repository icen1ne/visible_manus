# Multi-Agent 系统开发路线图

针对使用 Google ADK 或类似框架的实践路径

---

## 🎯 你的目标

> 理解 multi-agent 系统，然后使用 Google ADK (Agent Development Kit) 搭建自己的系统

---

## 📅 学习计划（推荐 2-4 周）

### Week 1: 理解和探索 (5-7 天)

#### Day 1-2: 概念学习
- [ ] 阅读 [TUTORIAL.md](./TUTORIAL.md) 第 1-2 章
- [ ] 理解 Multi-Agent 的核心概念
- [ ] 了解 ReAct 模式
- [ ] 画出系统架构图（用纸笔或工具）

**输出**: 一个你自己的架构图，标注清楚各组件的作用

#### Day 3-4: 运行现有项目
```bash
# 安装依赖
pip install -r requirements.txt
cd frontend && npm install

# 配置环境
echo "DEEPSEEK_API_KEY=your_key" > .env
echo "DEEPSEEK_URL=https://api.deepseek.com" >> .env

# 运行命令行版本
python main.py

# 或运行 Web 版本
python server.py  # 终端 1
cd frontend && npm run dev  # 终端 2
```

**任务**:
- [ ] 成功运行项目
- [ ] 测试 3-5 个不同的用户请求
- [ ] 观察 agent 如何协作
- [ ] 记录执行流程

**输出**: 一份观察笔记，记录系统如何处理请求

#### Day 5-7: 代码阅读
```
优先阅读顺序：
1. SIMPLE_EXAMPLE.py         ⭐⭐⭐ 先看这个！
2. core/task_manager.py      ⭐⭐⭐
3. agents/base_agent.py      ⭐⭐⭐
4. core/executor.py          ⭐⭐
5. planner/planner_agent.py  ⭐⭐
6. main.py (react_loop 函数) ⭐⭐
7. server.py                 ⭐
```

**任务**:
- [ ] 理解每个文件的作用
- [ ] 在代码中添加注释（中文）
- [ ] 追踪一个请求的完整数据流

**输出**: 带详细注释的代码副本

---

### Week 2: 动手实践 (5-7 天)

#### Day 8-10: 创建你的第一个 Agent

**目标**: 创建一个简单的 Agent（不使用 ADK）

```python
# my_first_agent.py

from agents.base_agent import BaseAgent

class CalculatorAgent(BaseAgent):
    """计算器 Agent - 处理数学问题"""

    def __init__(self):
        system_prompt = """
        你是一个数学计算助手。
        帮助用户解决数学问题。
        """
        super().__init__(system_prompt, allowed_servers=[])

# 测试
import asyncio

async def test():
    agent = CalculatorAgent()
    # 这里需要设置 mcp_client，可以先用 mock
    result = await agent.process("计算 123 * 456")
    print(result)

asyncio.run(test())
```

**任务**:
- [ ] 创建 2-3 个不同的 Agent
  - CalculatorAgent (数学)
  - SummarizerAgent (总结文本)
  - TranslatorAgent (翻译)
- [ ] 测试每个 Agent
- [ ] 理解 system_prompt 的作用

**输出**: 3 个可工作的 Agent

#### Day 11-12: 创建自己的工具

```python
# tools/my_calculator_server.py

from mcp.server.fastmcp import FastMCP

server = FastMCP("Calculator")

@server.tool()
def add(a: float, b: float) -> float:
    """加法"""
    return a + b

@server.tool()
def multiply(a: float, b: float) -> float:
    """乘法"""
    return a * b

if __name__ == "__main__":
    server.run()
```

**任务**:
- [ ] 创建一个 MCP 工具服务器
- [ ] 让 Agent 使用这个工具
- [ ] 测试工具调用

**输出**: 一个可工作的工具服务器 + Agent 调用示例

#### Day 13-14: 实现任务依赖

```python
# test_dependencies.py

from core.task_manager import TaskList, Task

# 创建任务列表
task_list = TaskList()
task_list.create_tasks([
    {
        "task_id": "t1",
        "agent": "ResearchAgent",
        "description": "研究主题 A",
        "dependencies": []
    },
    {
        "task_id": "t2",
        "agent": "SummarizerAgent",
        "description": "总结研究结果",
        "dependencies": ["t1"]  # 依赖 t1
    }
])

# 测试依赖执行
ready = task_list.get_ready_tasks()
print(f"可执行: {[t.task_id for t in ready]}")  # 应该只有 t1

# 完成 t1
task_list.mark_completed("t1", "研究结果...")

ready = task_list.get_ready_tasks()
print(f"可执行: {[t.task_id for t in ready]}")  # 现在应该有 t2
```

**任务**:
- [ ] 理解依赖关系的实现
- [ ] 创建复杂的依赖图
- [ ] 测试并发执行

**输出**: 一个有 4-5 个任务的依赖图，并成功执行

---

### Week 3: Google ADK 学习 (5-7 天)

#### Day 15-16: ADK 文档学习

**任务**:
- [ ] 阅读 Google ADK 官方文档
- [ ] 安装 ADK: `pip install google-agentic-development-kit` (假设)
- [ ] 运行 ADK 的 Hello World 示例
- [ ] 对比 ADK 和 Visible Manus 的架构

**创建对比表**:

| 功能 | Visible Manus | Google ADK |
|------|---------------|------------|
| Agent 基类 | BaseAgent | ? |
| 工具协议 | MCP | ? |
| 任务管理 | TaskManager | ? |
| LLM 调用 | LLMClient | ? |

**输出**: 填好的对比表 + ADK Hello World 运行成功

#### Day 17-18: 迁移你的 Agent 到 ADK

```python
# 示例：将 CalculatorAgent 迁移到 ADK
# (根据实际 ADK API 调整)

from google.adk import Agent, Tool

# 定义工具
@Tool
def calculate(expression: str) -> float:
    """计算数学表达式"""
    return eval(expression)  # 注意：实际使用中需要安全评估

# 创建 Agent
calculator_agent = Agent(
    name="CalculatorAgent",
    description="数学计算助手",
    tools=[calculate],
    model="gemini-pro"
)

# 使用 Agent
result = await calculator_agent.run("计算 123 * 456")
print(result)
```

**任务**:
- [ ] 迁移 Week 2 创建的 3 个 Agent
- [ ] 在 ADK 中实现工具调用
- [ ] 测试所有功能

**输出**: 3 个在 ADK 中工作的 Agent

#### Day 19-21: 实现 Multi-Agent 协作

```python
# multi_agent_with_adk.py

from google.adk import Agent, Orchestrator  # 假设 API

# 创建多个 Agent
research_agent = Agent(name="ResearchAgent", ...)
coder_agent = Agent(name="CoderAgent", ...)

# 创建编排器
orchestrator = Orchestrator()
orchestrator.register_agent(research_agent)
orchestrator.register_agent(coder_agent)

# 定义工作流
@orchestrator.workflow
async def research_and_code(user_request: str):
    # 1. 研究
    research_result = await research_agent.run(user_request)

    # 2. 编码（使用研究结果）
    code_result = await coder_agent.run(
        f"根据以下研究编写代码：\n{research_result}"
    )

    return code_result

# 执行
result = await orchestrator.execute(
    "研究 React Hooks 并编写示例"
)
```

**任务**:
- [ ] 实现 2-3 个 Agent 的协作
- [ ] 处理任务依赖（如果 ADK 支持）
- [ ] 实现错误处理

**输出**: 一个完整的 multi-agent 工作流

---

### Week 4: 构建完整项目 (5-7 天)

#### Day 22-24: 后端系统

**目标**: 构建一个小型但完整的 multi-agent 应用

**项目建议** (选一个):

1. **代码审查助手**
   - Agent 1: 读取代码
   - Agent 2: 检查安全问题
   - Agent 3: 检查性能问题
   - Agent 4: 生成审查报告

2. **内容创作系统**
   - Agent 1: 研究主题
   - Agent 2: 生成大纲
   - Agent 3: 撰写内容
   - Agent 4: 校对和优化

3. **数据分析管道**
   - Agent 1: 收集数据
   - Agent 2: 清洗数据
   - Agent 3: 分析数据
   - Agent 4: 生成报告

**任务**:
- [ ] 选择项目
- [ ] 设计架构
- [ ] 实现所有 Agent
- [ ] 实现协调逻辑
- [ ] 测试完整流程

**输出**: 可运行的 Python 应用

#### Day 25-26: 添加 WebSocket (可选)

```python
# simple_websocket_server.py

import asyncio
import websockets
import json

class AgentServer:
    def __init__(self):
        self.connections = set()

    async def broadcast(self, event_type: str, data: dict):
        """广播事件到所有客户端"""
        message = json.dumps({
            "type": event_type,
            "data": data
        })
        await asyncio.gather(*[
            ws.send(message)
            for ws in self.connections
        ])

    async def handle_client(self, websocket):
        """处理客户端连接"""
        self.connections.add(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                if data["type"] == "user_input":
                    # 启动 agent 处理
                    await self.process_request(data["text"])
        finally:
            self.connections.remove(websocket)

    async def process_request(self, user_input: str):
        """处理用户请求并广播状态"""
        await self.broadcast("agent_status", {
            "agent": "ResearchAgent",
            "status": "working"
        })

        # 执行 agent 任务...
        result = await research_agent.run(user_input)

        await self.broadcast("output", {
            "text": result
        })

# 启动服务器
server = AgentServer()
start_server = websockets.serve(server.handle_client, "localhost", 8765)
asyncio.run(start_server)
```

**任务**:
- [ ] 实现 WebSocket 服务器
- [ ] 在 agent 执行时广播状态
- [ ] 用浏览器控制台测试连接

#### Day 27-28: 前端可视化 (可选)

**简化版前端**:

```typescript
// App.tsx
import { useEffect, useState } from 'react';

function App() {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<string[]>([]);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8765');

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, `${data.type}: ${JSON.stringify(data.data)}`]);
    };

    setWs(socket);
  }, []);

  const sendMessage = () => {
    ws?.send(JSON.stringify({
      type: 'user_input',
      text: '测试请求'
    }));
  };

  return (
    <div>
      <button onClick={sendMessage}>发送测试</button>
      <div>
        {messages.map((msg, i) => (
          <div key={i}>{msg}</div>
        ))}
      </div>
    </div>
  );
}
```

**任务**:
- [ ] 创建简单的 React 应用
- [ ] 连接 WebSocket
- [ ] 显示 agent 状态
- [ ] (可选) 添加可视化

---

## 🎓 学习资源

### 必读文档
1. ✅ [TUTORIAL.md](./TUTORIAL.md) - 完整教程
2. ✅ [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - 快速参考
3. ✅ [SIMPLE_EXAMPLE.py](./SIMPLE_EXAMPLE.py) - 简化示例

### 推荐阅读
- **ReAct 论文**: "ReAct: Synergizing Reasoning and Acting in Language Models"
- **LangChain Docs**: 了解 Agent 和 Tool 的设计模式
- **Google ADK Docs**: 官方文档（发布后）

### 视频教程
- 搜索 "multi-agent system tutorial"
- 搜索 "LangChain agents"
- 搜索 "ReAct prompting"

### 开源项目参考
1. **LangGraph** - Agent 工作流
2. **AutoGen** - Multi-agent 对话
3. **CrewAI** - Role-based agents

---

## 🧪 练习项目

### 初级 (Week 2-3)
1. **天气助手**
   - Agent 查询天气 API
   - Agent 提供穿衣建议

2. **文本助手**
   - Agent 总结文本
   - Agent 翻译文本
   - Agent 提取关键词

3. **计算器**
   - Agent 解析数学表达式
   - Agent 执行计算
   - Agent 解释结果

### 中级 (Week 3-4)
1. **新闻摘要系统**
   - Agent 1: 搜索新闻
   - Agent 2: 提取关键信息
   - Agent 3: 生成摘要

2. **代码助手**
   - Agent 1: 分析代码
   - Agent 2: 提出改进建议
   - Agent 3: 生成重构版本

3. **学习助手**
   - Agent 1: 搜索学习资料
   - Agent 2: 生成学习大纲
   - Agent 3: 创建练习题

### 高级 (Month 2+)
1. **完整的客户服务系统**
   - 意图识别 Agent
   - 知识库查询 Agent
   - 响应生成 Agent
   - 质量检查 Agent

2. **自动化测试系统**
   - 需求分析 Agent
   - 测试用例生成 Agent
   - 测试执行 Agent
   - 报告生成 Agent

3. **内容审核系统**
   - 敏感词检测 Agent
   - 情感分析 Agent
   - 合规检查 Agent
   - 决策综合 Agent

---

## 📊 进度追踪

### Week 1 检查点
- [ ] 理解 Multi-Agent 核心概念
- [ ] 成功运行 Visible Manus
- [ ] 阅读完核心代码
- [ ] 能解释系统如何工作

### Week 2 检查点
- [ ] 创建了 3 个自定义 Agent
- [ ] 实现了工具调用
- [ ] 理解任务依赖关系
- [ ] 能独立实现简单的 multi-agent 流程

### Week 3 检查点
- [ ] 熟悉 Google ADK API
- [ ] 迁移了现有 Agent 到 ADK
- [ ] 实现了 multi-agent 协作
- [ ] 理解 ADK 的优势和限制

### Week 4 检查点
- [ ] 完成了一个完整项目
- [ ] (可选) 实现了 WebSocket 通信
- [ ] (可选) 创建了基础前端
- [ ] 能够独立设计和实现 multi-agent 系统

---

## 🎯 最终目标检查

完成路线图后，你应该能够：

### 理解层面 ✅
- [ ] 解释什么是 multi-agent 系统
- [ ] 说明 ReAct 模式的工作原理
- [ ] 理解任务依赖和并发执行
- [ ] 知道何时使用 multi-agent vs 单 agent

### 实践层面 ✅
- [ ] 使用 Google ADK 创建 Agent
- [ ] 定义和集成工具
- [ ] 实现多 Agent 协作
- [ ] 处理错误和边界情况

### 项目层面 ✅
- [ ] 从需求设计 agent 架构
- [ ] 实现完整的 agent 系统
- [ ] 部署和测试系统
- [ ] 优化性能和用户体验

---

## 🚀 下一步

完成这个路线图后：

1. **深入 ADK 特性**
   - 高级工具集成
   - 分布式 Agent
   - 生产级部署

2. **探索相关领域**
   - Prompt Engineering
   - RAG (检索增强生成)
   - Fine-tuning 模型

3. **构建实际产品**
   - 选择真实场景
   - 设计完整架构
   - 上线和迭代

4. **贡献开源**
   - 分享你的 Agent
   - 贡献到 ADK 社区
   - 写教程帮助他人

---

## 💬 获取帮助

### 遇到问题？

1. **检查文档**
   - TUTORIAL.md
   - QUICK_REFERENCE.md
   - Google ADK 官方文档

2. **查看示例**
   - SIMPLE_EXAMPLE.py
   - 项目中的其他 Agent

3. **调试技巧**
   - 打印中间结果
   - 查看 LLM 的实际调用
   - 使用 verbose 模式

4. **社区资源**
   - Google ADK 社区
   - Stack Overflow
   - GitHub Issues

---

**祝你学习顺利，构建出优秀的 Agent 系统！** 🎉

记住：
- 📖 先理解概念
- 💻 多动手实践
- 🔍 遇到问题多调试
- 🚀 持续迭代改进
