# Multi-Agent 系统完整教程

从零开始理解和搭建一个 multi-agent AI 协同系统

---

## 📚 目录

1. [什么是 Multi-Agent 系统？](#1-什么是-multi-agent-系统)
2. [项目整体架构](#2-项目整体架构)
3. [核心概念深入理解](#3-核心概念深入理解)
4. [前后端通信机制](#4-前后端通信机制)
5. [如何搭建自己的系统](#5-如何搭建自己的系统)
6. [使用 Google ADK 的建议](#6-使用-google-adk-的建议)

---

## 1. 什么是 Multi-Agent 系统？

### 1.1 简单理解

想象你是一个项目经理（Planner），你有几个专业的助手：
- **研究员（ResearchAgent）**：负责上网查资料
- **程序员（WebCoderAgent）**：负责写代码

当用户说："研究一下玻璃拟态设计风格，并创建一个示例网页"

**传统单 AI 方式**：一个 AI 试图完成所有事情，可能做得不够专业

**Multi-Agent 方式**：
1. 项目经理分析需求，制定计划
2. 让研究员去查资料
3. 研究完成后，让程序员根据研究结果写代码
4. 项目经理监督整个过程，随时调整计划

### 1.2 核心优势

✅ **专业化**：每个 agent 专注做一件事，做得更好
✅ **并行执行**：独立的任务可以同时进行
✅ **可扩展**：轻松添加新的专业 agent
✅ **可维护**：每个 agent 独立开发和测试

---

## 2. 项目整体架构

### 2.1 系统组件图

```
┌─────────────────────────────────────────────────────────────┐
│                         前端 (React)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  可视化画布   │  │  聊天输入框   │  │  消息日志     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                  WebSocket 实时通信                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↕ (ws://localhost:8765)
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                      后端 (Python)                           │
│  ┌────────────────────────────────────────────────────┐    │
│  │              WebSocket Server (server.py)           │    │
│  │            负责转发前端请求和后端事件                  │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                         │
│  ┌────────────────┴───────────────────────────────────┐    │
│  │         核心协调层 (main.py - ReAct Loop)           │    │
│  │                                                     │    │
│  │  ┌──────────┐  ┌──────────────┐  ┌──────────────┐ │    │
│  │  │ Planner  │→ │ TaskManager  │→ │  Executor    │ │    │
│  │  │ 计划制定  │  │  任务管理     │  │  任务执行     │ │    │
│  │  └──────────┘  └──────────────┘  └──────────────┘ │    │
│  │                       ↓                             │    │
│  │              ┌────────┴────────┐                   │    │
│  │              │  Agent Registry  │                   │    │
│  │              └────────┬────────┘                   │    │
│  │                       │                             │    │
│  │       ┌───────────────┼───────────────┐            │    │
│  │       ↓               ↓               ↓            │    │
│  │  ┌─────────┐  ┌──────────────┐  ┌─────────┐      │    │
│  │  │Research │  │  WebCoder    │  │  其他    │      │    │
│  │  │ Agent   │  │   Agent      │  │ Agents  │      │    │
│  │  └─────────┘  └──────────────┘  └─────────┘      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │           工具层 (MCP - Model Context Protocol)     │    │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐   │    │
│  │  │ Browser    │  │ File Writer│  │  Web Fetch │   │    │
│  │  │    MCP     │  │    MCP     │  │    MCP     │   │    │
│  │  └────────────┘  └────────────┘  └────────────┘   │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 目录结构解析

```
visible_manus/
│
├── frontend/                    # 前端 - React + Vite
│   ├── src/
│   │   ├── components/         # UI 组件
│   │   │   ├── Canvas/        # 可视化画布（节点和连线）
│   │   │   ├── Nodes/         # 不同类型的节点组件
│   │   │   └── Sidebar/       # 侧边栏（日志、历史）
│   │   ├── hooks/             # React Hooks
│   │   │   └── useWebSocket.ts # WebSocket 通信逻辑
│   │   ├── stores/            # Zustand 状态管理
│   │   └── types/             # TypeScript 类型定义
│   └── package.json
│
├── core/                       # 后端核心模块
│   ├── task_manager.py        # 任务管理（创建、修改、查询任务）
│   ├── executor.py            # 任务执行器（调度 agent 执行任务）
│   ├── llm_client.py          # LLM 客户端（与 AI 模型通信）
│   ├── mcp_client.py          # MCP 客户端（工具调用）
│   └── mcp_manager.py         # MCP 管理器（管理多个 MCP 服务器）
│
├── planner/                    # Planner Agent
│   └── planner_agent.py       # 计划制定：分解任务、动态调整
│
├── agents/                     # Specialist Agents
│   ├── base_agent.py          # Agent 基类
│   ├── research_agent.py      # 研究 Agent
│   └── web_coder_agent.py     # 编程 Agent
│
├── tools/                      # 工具服务器（MCP Servers）
│   └── mcp_servers/
│       ├── file_writer_server.py   # 文件写入工具
│       └── web_fetch_server.py     # 网页抓取工具
│
├── main.py                     # 后端主入口（命令行模式）
├── server.py                   # WebSocket 服务器（Web 模式）
└── requirements.txt            # Python 依赖
```

### 2.3 数据流动过程

```
用户输入 "研究玻璃拟态并创建网页"
    │
    ↓ (通过 WebSocket)
WebSocket Server 接收
    │
    ↓ (启动 ReAct Loop)
Planner 分析请求
    │
    ↓ (调用 create_task_list 工具)
创建任务列表：
    ├─ Task 1: ResearchAgent 去研究玻璃拟态
    └─ Task 2: WebCoderAgent 创建网页（依赖 Task 1）
    │
    ↓ (Executor 执行)
执行 Task 1:
    ResearchAgent 接收任务描述
    ├─ 调用 Browser MCP 打开浏览器
    ├─ 搜索相关信息
    ├─ 访问多个网页
    ├─ 提取内容
    └─ 返回研究报告
    │
    ↓ (Task 1 完成，依赖解除)
执行 Task 2:
    WebCoderAgent 接收任务描述 + Task 1 结果
    ├─ 分析研究报告
    ├─ 设计网页结构
    ├─ 调用 File Writer MCP 写入 HTML
    ├─ 调用 File Writer MCP 写入 CSS
    └─ 返回文件路径
    │
    ↓ (所有任务完成)
Planner 调用 finalize_plan
    │
    ↓ (通过 WebSocket)
前端显示最终结果和文件
```

---

## 3. 核心概念深入理解

### 3.1 任务管理系统（Task Manager）

**作用**：管理任务的生命周期

#### 任务的数据结构

```python
@dataclass
class Task:
    task_id: str              # 唯一标识符（如 "t1", "t2"）
    agent: str                # 负责执行的 Agent 名称
    description: str          # 任务描述（会作为 Agent 的 prompt）
    dependencies: List[str]   # 依赖的任务 ID 列表
    status: TaskStatus        # 状态：pending/executing/completed/failed
    result: Optional[str]     # 执行结果
    error: Optional[str]      # 错误信息
```

#### 依赖关系处理

```python
# 示例：两个任务
Task 1: {
    task_id: "t1",
    agent: "ResearchAgent",
    description: "研究玻璃拟态设计",
    dependencies: []  # 没有依赖，可以立即执行
}

Task 2: {
    task_id: "t2",
    agent: "WebCoderAgent",
    description: "根据研究创建网页",
    dependencies: ["t1"]  # 依赖 t1，必须等 t1 完成
}

# 执行流程：
# 1. TaskManager.get_ready_tasks() → 返回 [Task 1]
# 2. Executor 执行 Task 1
# 3. Task 1 完成后，TaskManager.get_ready_tasks() → 返回 [Task 2]
# 4. Executor 执行 Task 2（Task 1 的结果会自动传给 Task 2）
```

#### 核心方法

```python
# 创建任务列表
task_list.create_tasks([task1_dict, task2_dict])

# 获取可执行的任务（依赖已满足）
ready_tasks = task_list.get_ready_tasks()

# 标记任务状态
task_list.mark_executing(task_id)
task_list.mark_completed(task_id, result)
task_list.mark_failed(task_id, error)

# 动态调整
task_list.add_task(...)      # 添加新任务
task_list.modify_task(...)   # 修改任务
task_list.remove_task(...)   # 删除任务
```

### 3.2 Agent 系统

#### Agent 的基本结构

```python
class BaseAgent:
    def __init__(self, system_prompt: str, allowed_servers: list):
        self.system_prompt = system_prompt      # Agent 的角色定义
        self.allowed_servers = allowed_servers  # 可使用的工具
        self.llm_client = LLMClient()          # LLM 客户端

    async def process(self, prompt: str) -> str:
        """
        接收任务描述，返回执行结果

        内部流程：
        1. 将 prompt 包装成消息
        2. 调用 LLM（可能多轮对话）
        3. LLM 调用工具完成任务
        4. 返回最终结果
        """
        pass
```

#### ResearchAgent 示例

```python
# system_prompt（定义 Agent 身份）
RESEARCH_AGENT_PROMPT = """
你是一个专业的研究助手。
你的任务是：
1. 使用浏览器搜索相关信息
2. 访问多个可靠来源
3. 提取和综合信息
4. 生成结构化的研究报告

可用工具：
- navigate(url): 访问网页
- click(selector): 点击元素
- extract_content(): 提取页面内容
- google_search(query): 搜索
"""

# allowed_servers（可用工具）
allowed_servers = [
    ("browsermcp", {...})  # 浏览器控制工具
]

# 当执行任务时
task_description = "研究 Python asyncio，重点关注事件循环和最佳实践"
result = await research_agent.process(task_description)

# ResearchAgent 内部会：
# 1. 规划：决定搜索什么、访问哪些页面
# 2. 执行：调用浏览器工具
# 3. 综合：整理信息
# 4. 返回：结构化的研究报告
```

### 3.3 MCP (Model Context Protocol)

**什么是 MCP？**
- MCP 是一个标准协议，让 AI 可以安全地调用外部工具
- 类似于 API，但专门为 AI agent 设计

#### MCP Server 示例

```python
# tools/mcp_servers/file_writer_server.py
from mcp.server.fastmcp import FastMCP

server = FastMCP("FileWriter")

@server.tool()
def write_file(path: str, content: str) -> str:
    """写入文件"""
    with open(path, 'w') as f:
        f.write(content)
    return f"File written: {path}"

@server.tool()
def read_file(path: str) -> str:
    """读取文件"""
    with open(path, 'r') as f:
        return f.read()
```

#### Agent 如何使用 MCP 工具

```
Agent 向 LLM 发送消息：
    "请创建一个 index.html 文件"

LLM 返回工具调用：
    tool_call = {
        "function": {
            "name": "file_writer__write_file",
            "arguments": {
                "path": "output/index.html",
                "content": "<html>...</html>"
            }
        }
    }

MCP Client 执行工具：
    result = mcp_client.call_tool(tool_call)

结果返回给 LLM：
    "File written: output/index.html"

LLM 继续处理或结束任务
```

### 3.4 ReAct Loop（推理-行动循环）

**ReAct = Reasoning (推理) + Acting (行动)**

这是 Planner 的核心工作模式：

```python
# main.py - react_loop 函数

while not finished:
    # 1. Planner 推理（调用 LLM）
    response = await planner_client.chat(messages)

    # 2. Planner 决定行动（调用工具）
    if response has tool_call:
        if tool == "create_task_list":
            # 创建任务列表
            task_list.create_tasks(tasks)

        elif tool == "continue_execution":
            # 执行下一批任务
            results = await executor.execute_ready_tasks()

            # 3. 观察结果
            messages.append({"role": "user", "content": results})
            # 回到步骤 1，继续推理

        elif tool == "finalize_plan":
            # 完成，返回结果
            return final_response
```

**实际例子**：

```
Round 1:
  推理: "用户想研究并创建网页，需要两个任务"
  行动: create_task_list([task1, task2])
  观察: "Created 2 tasks"

Round 2:
  推理: "任务已创建，可以开始执行"
  行动: continue_execution()
  观察: (系统执行 task1)

Round 3:
  推理: "task1 已完成，结果是研究报告"
  行动: continue_execution()
  观察: (系统执行 task2)

Round 4:
  推理: "所有任务完成，网页已创建"
  行动: finalize_plan("已完成研究和网页创建...")
  观察: (结束)
```

---

## 4. 前后端通信机制

### 4.1 WebSocket 消息类型

#### 后端 → 前端的事件

```typescript
// server.py 发送，frontend/src/hooks/useWebSocket.ts 接收

事件类型                   作用                    数据
─────────────────────────────────────────────────────────────
session_start          会话开始                { user_input: string }
planner_status         Planner 状态更新        { status: 'working' | 'active' | ... }
thinking               Agent 思考内容          { agent: string, content: string }
tool_call              工具调用开始            { agent, tool, args, id }
tool_call_complete     工具调用完成            { agent, id }
tasks_update           任务列表更新            { tasks: Task[] }
task_status            单个任务状态更新         { task_id, status, result? }
agent_status           Agent 状态更新          { agent, status }
agent_task             Agent 开始任务          { agent, task }
output                 最终输出                { text, files }
session_end            会话结束                { status, output? }
error                  错误信息                { message }
```

#### 前端 → 后端的消息

```typescript
// 用户输入
send({
  type: 'user_input',
  text: '研究玻璃拟态并创建网页'
})

// 心跳（保持连接）
send({ type: 'ping' })
```

### 4.2 前端状态管理（Zustand）

```typescript
// frontend/src/stores/systemStore.ts

interface SystemStore {
  // 输入节点
  inputText: string
  inputStatus: NodeStatus

  // Planner 节点
  plannerStatus: NodeStatus
  plannerThinking: string
  plannerToolCall?: ToolCall

  // 任务列表
  tasks: Task[]

  // Agent 节点
  researchAgentStatus: NodeStatus
  researchAgentTask?: Task
  researchAgentToolCalls: ToolCall[]

  webCoderAgentStatus: NodeStatus
  webCoderAgentTask?: Task
  webCoderAgentToolCalls: ToolCall[]

  // 输出节点
  outputStatus: NodeStatus
  outputText: string
  outputFiles: string[]

  // 消息日志
  messages: Message[]

  // 动作
  setInputText: (text: string) => void
  setPlannerStatus: (status: NodeStatus) => void
  addMessage: (message: Message) => void
  // ... 更多动作
}
```

### 4.3 实时可视化流程

```
用户在前端输入 → ChatInput 组件
    │
    ↓ send({ type: 'user_input', text: '...' })
WebSocket 发送到后端
    │
    ↓ server.py 接收并启动 react_loop
后端开始处理
    │
    ├─→ broadcast('session_start', {...})      → 前端：InputNode 激活
    ├─→ broadcast('planner_status', 'working') → 前端：PlannerNode 显示"工作中"
    ├─→ broadcast('thinking', {...})           → 前端：PlannerNode 显示思考内容
    ├─→ broadcast('tool_call', {...})          → 前端：PlannerNode 显示工具调用
    ├─→ broadcast('tasks_update', {...})       → 前端：TaskListNode 显示任务列表
    ├─→ broadcast('agent_status', 'working')   → 前端：ResearchAgentNode 激活
    ├─→ broadcast('tool_call', {...})          → 前端：ResearchAgentNode 显示工具调用
    ├─→ broadcast('task_status', 'completed')  → 前端：TaskListNode 更新任务状态
    ├─→ broadcast('agent_status', 'working')   → 前端：WebCoderAgentNode 激活
    └─→ broadcast('output', {...})             → 前端：OutputNode 显示结果
```

### 4.4 连线动画

```typescript
// frontend/src/components/Canvas/ConnectionLines.tsx

// 根据节点状态动态绘制连线
const connections = [
  // Input → Planner
  {
    from: 'input',
    to: 'planner',
    active: inputStatus === 'active'  // 激活时动画流动
  },

  // Planner → TaskList
  {
    from: 'planner',
    to: 'task-list',
    active: plannerStatus === 'working' || tasks.length > 0
  },

  // TaskList → ResearchAgent（当 task1 执行时）
  {
    from: 'task-list',
    to: 'research-agent',
    active: researchAgentTask !== undefined
  },

  // ... 更多连线
]
```

---

## 5. 如何搭建自己的系统

### 5.1 最小可行系统（MVP）

**第一步：核心组件**

```python
# 1. 任务管理器
class SimpleTaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task_id, description, agent):
        self.tasks.append({
            'id': task_id,
            'description': description,
            'agent': agent,
            'status': 'pending'
        })

    def get_next_task(self):
        for task in self.tasks:
            if task['status'] == 'pending':
                return task
        return None

# 2. 简单 Agent
class SimpleAgent:
    def __init__(self, name):
        self.name = name

    async def execute(self, task_description):
        # 调用 LLM API
        response = await call_llm_api(task_description)
        return response

# 3. 协调器
class SimpleOrchestrator:
    def __init__(self):
        self.task_manager = SimpleTaskManager()
        self.agents = {}

    def register_agent(self, name, agent):
        self.agents[name] = agent

    async def run(self, user_request):
        # 1. 规划任务（简化版：手动或用 LLM 生成）
        tasks = await self.plan_tasks(user_request)
        for task in tasks:
            self.task_manager.add_task(task['id'], task['description'], task['agent'])

        # 2. 执行任务
        while True:
            task = self.task_manager.get_next_task()
            if not task:
                break

            agent = self.agents[task['agent']]
            result = await agent.execute(task['description'])

            task['status'] = 'completed'
            task['result'] = result

        # 3. 返回结果
        return self.format_results()
```

### 5.2 逐步增强

#### 阶段 1：基础版（1-2 天）
- ✅ 单个 Agent
- ✅ 简单任务执行
- ✅ 命令行交互

```python
# 示例
agent = SimpleAgent("assistant")
result = await agent.execute("查询今天的天气")
print(result)
```

#### 阶段 2：多 Agent（3-5 天）
- ✅ 多个专业 Agent
- ✅ 任务依赖关系
- ✅ 基础协调逻辑

```python
# 示例
orchestrator = SimpleOrchestrator()
orchestrator.register_agent("researcher", ResearchAgent())
orchestrator.register_agent("coder", CoderAgent())

await orchestrator.run("研究 React Hooks 并写示例代码")
```

#### 阶段 3：工具集成（5-7 天）
- ✅ MCP 工具支持
- ✅ 文件操作
- ✅ 网页浏览

```python
# 示例：Agent 可以调用工具
research_agent = ResearchAgent()
research_agent.add_tool("web_search", web_search_tool)
research_agent.add_tool("browse", browser_tool)
```

#### 阶段 4：动态规划（7-10 天）
- ✅ ReAct Loop
- ✅ Planner Agent
- ✅ 动态调整任务

```python
# 示例：系统可以根据中间结果调整计划
planner = PlannerAgent()
plan = await planner.create_plan(user_request)

while not plan.is_complete():
    results = await execute_next_batch(plan)
    plan = await planner.adjust_plan(plan, results)
```

#### 阶段 5：可视化前端（10-14 天）
- ✅ WebSocket 通信
- ✅ 实时状态显示
- ✅ 交互式界面

### 5.3 关键技术栈选择

#### 后端
```
Python 生态：
├─ LLM 调用: OpenAI SDK / Anthropic SDK / LangChain
├─ 异步编程: asyncio
├─ WebSocket: websockets / FastAPI WebSocket
└─ 工具协议: MCP / LangChain Tools

其他语言：
├─ TypeScript: LangChain.js / AI SDK
├─ Go: 自定义 agent 框架
└─ Java: Spring AI / LangChain4j
```

#### 前端
```
React 生态：
├─ UI 框架: React / Vue / Svelte
├─ 状态管理: Zustand / Redux / Jotai
├─ 可视化: React Flow / D3.js / Canvas API
└─ 实时通信: WebSocket / Server-Sent Events
```

### 5.4 核心挑战和解决方案

#### 挑战 1：错误处理
```python
# ❌ 坏的做法
result = await agent.execute(task)
task.mark_completed(result)

# ✅ 好的做法
try:
    result = await agent.execute(task)
    task.mark_completed(result)
except Exception as e:
    task.mark_failed(str(e))
    # 重试逻辑
    if task.retry_count < 3:
        task.retry()
    else:
        # 通知 Planner 调整计划
        await planner.handle_task_failure(task)
```

#### 挑战 2：超时控制
```python
import asyncio

# 设置超时
try:
    result = await asyncio.wait_for(
        agent.execute(task),
        timeout=300  # 5 分钟超时
    )
except asyncio.TimeoutError:
    task.mark_failed("Task timeout")
```

#### 挑战 3：并发执行
```python
# 找出所有无依赖的任务
ready_tasks = task_manager.get_ready_tasks()

# 并发执行
results = await asyncio.gather(*[
    self.execute_task(task)
    for task in ready_tasks
])
```

#### 挑战 4：上下文传递
```python
# 依赖任务的结果自动传递
async def execute_task(self, task):
    # 收集依赖任务的结果
    context = ""
    for dep_id in task.dependencies:
        dep_task = task_manager.get_task(dep_id)
        context += f"\n\n[Result from {dep_id}]\n{dep_task.result}"

    # 将上下文加入 prompt
    full_prompt = f"{task.description}\n\n[Context]{context}"

    result = await agent.execute(full_prompt)
    return result
```

---

## 6. 使用 Google ADK 的建议

### 6.1 ADK 核心概念映射

```
Visible Manus 概念          →  Google ADK 概念
──────────────────────────────────────────────
Planner Agent              →  Orchestrator Agent
BaseAgent                  →  BaseAgent / Custom Agent
MCP Server                 →  Tool / Function Calling
TaskManager                →  WorkflowManager (可能需要自己实现)
LLMClient                  →  ADK Client
```

### 6.2 使用 ADK 的优势

✅ **内置功能**：
- Agent 生命周期管理
- 工具调用框架
- 错误处理和重试
- 日志和监控

✅ **与 Google 服务集成**：
- Gemini 模型
- Vertex AI
- Google Cloud Storage

✅ **企业级特性**：
- 安全性和权限控制
- 扩展性和负载均衡

### 6.3 迁移建议

#### 步骤 1：理解 ADK 架构
```python
# 阅读 ADK 文档，理解：
- 如何创建 Agent
- 如何定义 Tool
- 如何编排多个 Agent
- 如何处理对话历史
```

#### 步骤 2：创建第一个 Agent
```python
# 伪代码（根据 ADK 实际 API）
from google.adk import Agent, Tool

# 定义工具
@Tool
def web_search(query: str) -> str:
    # 实现搜索逻辑
    return search_results

# 创建 Agent
research_agent = Agent(
    name="ResearchAgent",
    description="专业研究助手",
    tools=[web_search],
    model="gemini-pro"
)

# 执行任务
result = await research_agent.run("研究 AI 最新趋势")
```

#### 步骤 3：实现任务依赖
```python
# 如果 ADK 没有内置任务管理，可以自己实现
class TaskGraph:
    def __init__(self):
        self.tasks = {}
        self.results = {}

    def add_task(self, task_id, agent, prompt, depends_on=[]):
        self.tasks[task_id] = {
            'agent': agent,
            'prompt': prompt,
            'depends_on': depends_on
        }

    async def execute(self):
        while self.tasks:
            # 找到可以执行的任务
            ready = [
                task_id for task_id, task in self.tasks.items()
                if all(dep in self.results for dep in task['depends_on'])
            ]

            # 并发执行
            results = await asyncio.gather(*[
                self.execute_task(task_id)
                for task_id in ready
            ])

            # 保存结果
            for task_id, result in zip(ready, results):
                self.results[task_id] = result
                del self.tasks[task_id]
```

#### 步骤 4：添加 Orchestrator
```python
orchestrator_agent = Agent(
    name="Orchestrator",
    description="任务规划和协调",
    tools=[create_task, execute_task, finalize],
    model="gemini-pro"
)

# Orchestrator 决定创建哪些任务，如何编排
plan = await orchestrator_agent.run(user_request)
```

### 6.4 ADK 特定注意事项

1. **成本优化**：
   - 对简单任务使用较小的模型
   - 缓存重复的查询
   - 批量处理

2. **延迟优化**：
   - 流式输出（如果支持）
   - 并行调用
   - 预加载常用工具

3. **可观测性**：
   - 集成 Google Cloud Logging
   - 使用 OpenTelemetry 追踪
   - 监控 agent 性能

---

## 7. 总结和下一步

### 7.1 核心要点回顾

1. **Multi-Agent 本质**：将复杂任务分解给专业 Agent
2. **任务管理**：依赖图、状态跟踪、动态调整
3. **ReAct 模式**：推理-行动-观察的循环
4. **工具集成**：通过 MCP 或类似协议让 AI 调用外部工具
5. **实时通信**：WebSocket 实现前后端同步

### 7.2 学习路径

```
初学者路径（2-4 周）：
Week 1: 理解概念，运行现有项目
Week 2: 创建单个 Agent 和简单工具
Week 3: 实现任务依赖和多 Agent 协作
Week 4: 添加前端可视化

进阶路径（1-2 个月）：
Month 1: 实现完整的 ReAct Loop 和动态规划
Month 2: 生产级特性（错误处理、监控、扩展性）

专家路径（3+ 个月）：
- 自定义 Agent 架构
- 复杂工具集成（数据库、API、云服务）
- 分布式 Agent 系统
- 安全性和权限控制
```

### 7.3 推荐资源

**论文和文章**：
- ReAct: Synergizing Reasoning and Acting in Language Models
- AutoGPT: 自主 Agent 系统
- LangChain: Agent 和工具链

**开源项目**：
- LangGraph: Agent 工作流框架
- AutoGen: Multi-Agent 对话框架
- CrewAI: Role-based Agent 协作

**实践项目**：
1. 构建一个代码审查 Agent 系统
2. 创建一个客户服务 Agent 编排
3. 实现一个数据分析 Agent 管道

### 7.4 常见问题

**Q: 何时需要 Multi-Agent？**
A: 当任务可以明确分解为多个专业子任务，且每个子任务受益于专门的 prompt 和工具时。

**Q: 单个强大的 Agent 不够吗？**
A: 理论上可以，但实践中多个专业 Agent 更易维护、测试和扩展。

**Q: 如何避免 Agent 之间的死锁？**
A: 仔细设计依赖图，确保无环；添加超时机制；实现优雅降级。

**Q: 前端可视化是必需的吗？**
A: 不是，但它大大提升了调试体验和用户体验。可以先用命令行，后续再添加 UI。

---

**祝你构建 Agent 系统顺利！** 🚀

如有问题，可以：
1. 查看代码注释
2. 运行示例项目
3. 阅读相关文档
4. 实践、实践、再实践
