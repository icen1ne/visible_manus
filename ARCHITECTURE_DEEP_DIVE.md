# Multi-Agent 系统架构深度解析

深入理解系统设计理念和组件关系

---

## 问题 1: Planner Agent 的特殊地位

### 为什么 Planner 要单独放？

**你的理解完全正确！** Planner Agent 确实是"调度一切的主 Agent"。

### 架构层次

```
┌─────────────────────────────────────────────────────────────┐
│                    系统架构层次                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  第 1 层: 协调层 (Orchestration Layer)                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │          Planner Agent (主 Agent)                   │    │
│  │                                                    │    │
│  │  职责:                                             │    │
│  │  • 理解用户需求                                     │    │
│  │  • 分解为子任务                                     │    │
│  │  • 决定使用哪些 Sub Agent                          │    │
│  │  • 审查执行结果                                     │    │
│  │  • 动态调整计划                                     │    │
│  │  • 决定何时结束                                     │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓ 指挥                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Core 执行引擎                          │    │
│  │  ┌──────────────┐  ┌──────────────┐               │    │
│  │  │TaskManager   │  │  Executor    │               │    │
│  │  │任务队列管理   │→ │  任务执行    │               │    │
│  │  └──────────────┘  └──────────────┘               │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓ 调用                             │
│  第 2 层: 执行层 (Execution Layer)                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Sub Agents (专业 Agent)                     │    │
│  │                                                    │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  │    │
│  │  │ Research    │  │  WebCoder   │  │  Analyst │  │    │
│  │  │   Agent     │  │   Agent     │  │   Agent  │  │    │
│  │  └─────────────┘  └─────────────┘  └──────────┘  │    │
│  │                                                    │    │
│  │  职责:                                             │    │
│  │  • 接收具体任务描述                                 │    │
│  │  • 调用工具完成任务                                 │    │
│  │  • 返回执行结果                                     │    │
│  │  • 不需要知道整体计划                               │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 为什么这样分层？

#### 1. **关注点分离 (Separation of Concerns)**

```python
# Planner Agent 关注的问题
"用户想要什么？"
"需要哪些步骤？"
"哪个 Agent 适合这个任务？"
"执行顺序是什么？"
"结果是否满足预期？"

# Sub Agent 关注的问题
"这个任务具体怎么做？"
"需要调用哪些工具？"
"如何处理错误？"
"结果格式是什么？"
```

**类比**:
- **Planner** = 项目经理（看全局，做决策）
- **Sub Agents** = 工程师（做具体工作）

#### 2. **单一职责原则 (Single Responsibility Principle)**

```python
# ❌ 如果不分离
class MonolithicAgent:
    def process(self, user_request):
        # 1. 理解需求（Planner 的职责）
        # 2. 分解任务（Planner 的职责）
        # 3. 做研究（ResearchAgent 的职责）
        # 4. 写代码（CoderAgent 的职责）
        # 5. 审查结果（Planner 的职责）
        # 太复杂！一个 Agent 做所有事

# ✅ 分离后
class PlannerAgent:
    def plan(self, user_request):
        # 只负责规划和调度
        pass

class ResearchAgent:
    def research(self, topic):
        # 只负责研究
        pass

class CoderAgent:
    def code(self, requirements):
        # 只负责编码
        pass
```

#### 3. **可扩展性**

```python
# 添加新的 Sub Agent 很容易
class TranslatorAgent(BaseAgent):
    """新的翻译 Agent"""
    pass

# Planner 自动可以使用它
# 只需要在 system prompt 中告诉 Planner 有这个 Agent
```

#### 4. **可测试性**

```python
# 可以独立测试每个组件
def test_research_agent():
    agent = ResearchAgent()
    result = await agent.process("研究 Python")
    assert "Python" in result

def test_planner():
    planner = PlannerAgent()
    tasks = await planner.create_plan("研究 Python 并写代码")
    assert len(tasks) == 2
    assert tasks[0].agent == "ResearchAgent"
    assert tasks[1].agent == "CoderAgent"
```

### Planner 的独特之处

#### Planner 是唯一有"上帝视角"的 Agent

```python
# Planner 知道:
- 所有可用的 Sub Agents
- 整体任务目标
- 已完成的任务和结果
- 待执行的任务
- 任务之间的依赖关系

# Sub Agent 只知道:
- 当前任务描述
- 依赖任务的结果（作为上下文）
- 自己可用的工具
```

**实际例子**:

```
用户请求: "研究 React Hooks 并创建示例网页"

Planner 的思考过程:
1. 分析: 这需要两步
   - 先研究（信息收集）
   - 后编码（生成网页）
2. 决定:
   - Task 1 → ResearchAgent（研究）
   - Task 2 → WebCoderAgent（编码，依赖 Task 1）
3. 执行后审查:
   - Task 1 结果包含足够信息吗？
   - Task 2 生成的网页符合要求吗？
   - 需要补充任务吗？

ResearchAgent 的思考:
- 只看到: "研究 React Hooks 的用法和最佳实践"
- 不知道: 为什么要研究，结果会给谁用
- 只管: 做好研究，返回报告

WebCoderAgent 的思考:
- 只看到: "根据研究创建网页" + (Task 1 的结果作为上下文)
- 不知道: 为什么用户想要这个网页
- 只管: 生成高质量的代码
```

---

## 问题 2: Core 文件夹设计理念

### 从零到一的设计过程

让我们重现设计思路：

#### 步骤 1: 识别核心需求

```
用户需求: 让多个 AI Agent 协作完成复杂任务

问题拆解:
1. 如何表示"任务"？
2. 如何管理多个任务？
3. 如何执行任务？
4. 如何让 Agent 调用工具？
5. 如何与 LLM 通信？
```

#### 步骤 2: 设计数据结构

```python
# task_manager.py - 解决"如何表示和管理任务"

# 问题: 任务是什么？
# 答案: 任务是一个数据结构
@dataclass
class Task:
    task_id: str          # 唯一标识
    agent: str            # 谁来做
    description: str      # 做什么
    dependencies: List    # 依赖谁
    status: TaskStatus    # 当前状态
    result: Optional[str] # 结果

# 问题: 如何管理多个任务？
# 答案: TaskList 类
class TaskList:
    def create_tasks(...)      # 创建任务列表
    def get_ready_tasks(...)   # 找出可执行的任务
    def mark_completed(...)    # 标记完成
```

#### 步骤 3: 设计执行引擎

```python
# executor.py - 解决"如何执行任务"

class TaskExecutor:
    """
    职责:
    1. 从 TaskManager 获取就绪任务
    2. 找到对应的 Agent
    3. 调用 Agent 执行
    4. 处理结果和错误
    5. 更新任务状态
    """

    def __init__(self, task_list, agents):
        self.task_list = task_list    # 任务管理器
        self.agents = agents          # Agent 注册表

    async def execute_ready_tasks(self):
        # 1. 获取可执行任务
        ready = self.task_list.get_ready_tasks()

        # 2. 并发执行
        results = await asyncio.gather(*[
            self.execute_task(task)
            for task in ready
        ])

        return results

    async def execute_task(self, task):
        # 1. 找到 Agent
        agent = self.agents[task.agent]

        # 2. 准备上下文（依赖任务的结果）
        context = self._get_context(task)

        # 3. 执行
        result = await agent.process(task.description + context)

        # 4. 更新状态
        self.task_list.mark_completed(task.task_id, result)

        return result
```

#### 步骤 4: 设计 LLM 通信层

```python
# llm_client.py - 解决"如何与 LLM 通信"

class LLMClient:
    """
    职责:
    1. 封装 LLM API 调用
    2. 处理工具调用（Function Calling）
    3. 管理对话历史
    4. 错误处理和重试
    """

    async def chat(self, messages, allowed_servers=None):
        # 1. 准备请求
        request = {
            "model": self.model,
            "messages": messages
        }

        # 2. 如果有工具，加入 tools 参数
        if allowed_servers:
            tools = self._get_tools(allowed_servers)
            request["tools"] = tools

        # 3. 调用 LLM API
        response = await self.api_client.chat.completions.create(**request)

        # 4. 处理响应
        if response.has_tool_calls():
            # 执行工具调用
            tool_results = await self._execute_tools(response.tool_calls)
            # 将结果加入对话
            messages.extend(tool_results)
            # 继续对话
            return await self.chat(messages, allowed_servers)
        else:
            # 返回最终响应
            return response.content
```

#### 步骤 5: 设计 MCP 集成

```python
# mcp_client.py + mcp_manager.py - 解决"如何让 Agent 调用工具"

class MCPManager:
    """
    职责:
    1. 管理多个 MCP 服务器
    2. 启动/关闭服务器
    3. 提供统一的工具调用接口
    """

class MCPClient:
    """
    职责:
    1. 与 MCP 服务器通信
    2. 列出可用工具
    3. 执行工具调用
    """
```

### Core 文件夹的设计哲学

```
core/
├── task_manager.py    # 数据层 - 任务的表示和管理
├── executor.py        # 执行层 - 任务的调度和执行
├── llm_client.py      # 通信层 - 与 LLM 的交互
├── mcp_client.py      # 工具层 - 工具调用的客户端
└── mcp_manager.py     # 工具层 - 工具服务的管理

设计原则:
1. 分层架构（数据、执行、通信、工具）
2. 单一职责（每个模块只做一件事）
3. 低耦合（模块之间通过接口交互）
4. 高内聚（相关功能放在一起）
```

### 完整工作流程

```python
# main.py - 整合所有组件

async def react_loop(user_request):
    """ReAct 主循环"""

    # 1. 初始化
    task_list = TaskList()
    executor = TaskExecutor(task_list, agents)

    # 2. Planner 开始规划
    planner_messages = [
        {"role": "system", "content": PLANNER_PROMPT},
        {"role": "user", "content": user_request}
    ]

    while True:
        # 3. Planner 推理（调用 LLM）
        response = await planner_client.chat(
            planner_messages,
            allowed_servers=[("planner", "path/to/planner.py")]
        )
        #    ↑
        #    llm_client.py 负责这个调用

        planner_messages.extend(response)
        last_message = planner_messages[-1]

        # 4. 处理 Planner 的工具调用
        if last_message["role"] == "tool":
            tool_result = last_message["content"]

            if "CONTINUE" in tool_result:
                # 5. Executor 执行任务
                results = await executor.execute_ready_tasks()
                #                ↑
                #                executor.py 负责调度
                #                task_manager.py 负责任务状态

                # 6. 反馈给 Planner
                planner_messages.append({
                    "role": "user",
                    "content": f"执行结果: {results}"
                })
                # 回到步骤 3，继续循环

            elif "FINALIZED" in tool_result:
                # 完成
                return extract_final_response(tool_result)
```

### 各组件的角色

#### 1. **task_manager.py** - "任务数据库"

```python
职责:
- 存储任务数据
- 管理任务状态
- 处理依赖关系
- 查询可执行任务

不负责:
- ❌ 执行任务（Executor 的职责）
- ❌ 创建任务计划（Planner 的职责）
- ❌ 与 LLM 通信（LLMClient 的职责）
```

#### 2. **executor.py** - "任务调度器"

```python
职责:
- 从 TaskManager 获取任务
- 找到对应的 Agent
- 准备任务上下文（依赖结果）
- 调用 Agent 执行
- 处理执行结果
- 更新任务状态

不负责:
- ❌ 决定创建哪些任务（Planner 的职责）
- ❌ 具体的任务执行逻辑（Agent 的职责）
- ❌ 直接调用 LLM（通过 Agent 调用）
```

#### 3. **llm_client.py** - "LLM API 包装器"

```python
职责:
- 封装 LLM API（OpenAI, Anthropic, DeepSeek 等）
- 处理 Function Calling / Tool Use
- 管理对话历史
- 自动处理多轮对话（直到不再调用工具）
- 错误处理和重试

不负责:
- ❌ 决定调用哪些工具（由 LLM 决定）
- ❌ 任务管理（TaskManager 的职责）
- ❌ Agent 逻辑（Agent 的职责）
```

**你的理解完全正确！** llm_client.py 就是 LLM API 的接口封装。

#### 4. **mcp_client.py & mcp_manager.py** - "工具调用基础设施"

```python
职责:
- 启动和管理 MCP 服务器进程
- 列出服务器提供的工具
- 执行工具调用
- 处理工具执行结果

不负责:
- ❌ 决定调用哪个工具（LLM 决定）
- ❌ 实现工具逻辑（MCP 服务器实现）
```

### Planner 如何介入工作流

```python
# 详细的工作流程

# === 步骤 1: 用户输入 ===
user_request = "研究 React Hooks 并创建网页"

# === 步骤 2: Planner 分析 ===
# main.py 调用 planner_client
response = await planner_client.chat(
    messages=[
        {"role": "system", "content": PLANNER_PROMPT},
        {"role": "user", "content": user_request}
    ],
    allowed_servers=[("planner", "path/to/planner_agent.py")]
)
#    ↓
#    llm_client.py 内部:
#    1. 调用 LLM API
#    2. LLM 看到 PLANNER_PROMPT，知道自己是 Planner
#    3. LLM 看到可用工具（从 planner_agent.py MCP 服务器获取）:
#       - create_task_list
#       - add_task
#       - continue_execution
#       - finalize_plan
#    4. LLM 决定调用 create_task_list 工具

# === 步骤 3: Planner 调用工具 ===
# LLM 返回:
tool_call = {
    "function": {
        "name": "planner__create_task_list",
        "arguments": json.dumps({
            "tasks": [
                {
                    "task_id": "t1",
                    "agent": "ResearchAgent",
                    "description": "研究 React Hooks...",
                    "dependencies": []
                },
                {
                    "task_id": "t2",
                    "agent": "WebCoderAgent",
                    "description": "创建网页...",
                    "dependencies": ["t1"]
                }
            ]
        })
    }
}

# llm_client.py 执行这个工具调用:
# → 调用 planner_agent.py 的 create_task_list 函数
# → 该函数内部调用 TaskManager.create_tasks()
# → 任务被保存到 tmp/task_list.json

# === 步骤 4: 系统执行任务 ===
# main.py 看到工具返回结果，触发执行
task_list = TaskList.load("tmp/task_list.json")
executor.task_list = task_list

results = await executor.execute_ready_tasks()
#    ↓
#    executor.py 内部:
#    1. task_list.get_ready_tasks() → 返回 [Task t1]
#    2. 找到 ResearchAgent
#    3. 调用 agent.process(t1.description)
#       ↓
#       agent 内部:
#       - 调用 llm_client.chat()
#       - LLM 看到 ResearchAgent 的 system_prompt
#       - LLM 看到可用工具（browsermcp）
#       - LLM 决定调用 navigate, search 等工具
#       - 完成研究，返回结果
#    4. executor 标记 t1 完成

# === 步骤 5: 继续执行 ===
# main.py 将结果反馈给 Planner
planner_messages.append({
    "role": "user",
    "content": f"Task t1 完成: {result}"
})

# Planner 推理
response = await planner_client.chat(planner_messages)
# LLM 决定: 调用 continue_execution 工具

# 系统继续执行 t2...
# t2 完成后，Planner 调用 finalize_plan

# === 步骤 6: 结束 ===
return final_result
```

### 在哪个环节决定使用哪个 Agent？

```python
# === 答案: 在 Planner 创建任务时决定 ===

# planner_agent.py 的 PLANNER_PROMPT 告诉 LLM 有哪些 Agent:
"""
可用 Agents:
- ResearchAgent: 网络研究
- WebCoderAgent: 代码生成
- AnalystAgent: 数据分析
"""

# Planner (LLM) 根据任务性质决定:
LLM 思考: "用户要研究，应该用 ResearchAgent"
LLM 创建: {
    "task_id": "t1",
    "agent": "ResearchAgent",  # ← Planner 决定
    "description": "研究..."
}

# Executor 只是按照 task.agent 字段找到对应的 Agent 实例
agent = self.agents[task.agent]  # agents["ResearchAgent"]
```

### Agent 在 ReAct Loop 中如何决定使用工具？

```python
# === 答案: Agent 的 LLM 决定 ===

# 例如 ResearchAgent
class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt=RESEARCH_PROMPT,  # 告诉 LLM 角色
            allowed_servers=[("browsermcp", ...)]  # 可用工具
        )

# 当 executor 调用
result = await research_agent.process("研究 React Hooks")

# 内部流程（base_agent.py）:
async def process(self, prompt):
    messages = [
        {"role": "system", "content": self.system_prompt},
        {"role": "user", "content": prompt}
    ]

    # ReAct Loop（在 Agent 内部）
    while True:
        # 1. 调用 LLM
        response = await self.llm_client.chat(
            messages,
            allowed_servers=self.allowed_servers
        )
        #    ↓
        #    llm_client.py 内部:
        #    - LLM 看到 RESEARCH_PROMPT，知道自己是研究助手
        #    - LLM 看到可用工具（browsermcp 的工具列表）
        #    - LLM 决定: "我应该先搜索"
        #    - LLM 返回 tool_call: navigate("google.com")

        # 2. llm_client 自动执行工具
        #    - 调用 browsermcp 的 navigate 工具
        #    - 获得结果
        #    - 加入 messages
        #    - 再次调用 LLM

        # 3. LLM 继续推理
        #    - 看到导航结果
        #    - 决定: "现在搜索"
        #    - 返回 tool_call: search("React Hooks")

        # 4. 重复，直到 LLM 不再调用工具
        #    - LLM 决定: "我已经收集足够信息"
        #    - 返回文本内容（不是 tool_call）
        #    - ReAct Loop 结束

        # 5. 返回结果
        if no_more_tool_calls:
            return final_response
```

---

## 问题 3: 为什么需要任务管理器？

### 任务 ≠ Session

**重要区分**:

```python
# Session（会话）
- 定义: 用户的一次完整交互
- 生命周期: 从用户输入到最终结果
- 数量: 一个 Session

# Task（任务）
- 定义: Session 中的一个子任务
- 生命周期: 从创建到完成
- 数量: 一个 Session 可能有多个 Tasks

示例:
Session: "研究 React Hooks 并创建网页"
  ├─ Task 1: 研究 React Hooks
  └─ Task 2: 创建网页（依赖 Task 1）
```

### 为什么必须有任务管理器？

#### 场景 1: 无任务管理器（单 Agent 系统）

```python
# ❌ 简单但限制多
class SimpleSystem:
    async def process(self, user_request):
        # 一个 Agent 做所有事
        response = await agent.chat(user_request)
        return response

# 问题:
# 1. 无法利用专业 Agent
# 2. 无法并发执行
# 3. 无法处理复杂依赖
# 4. 难以追踪进度
# 5. 无法动态调整
```

#### 场景 2: 有任务管理器（Multi-Agent 系统）

```python
# ✅ 灵活且强大
class MultiAgentSystem:
    async def process(self, user_request):
        # 1. Planner 创建任务列表
        tasks = await planner.plan(user_request)
        task_manager.add_tasks(tasks)

        # 2. 按依赖关系执行
        while task_manager.has_pending_tasks():
            ready = task_manager.get_ready_tasks()
            # 并发执行所有就绪任务
            await asyncio.gather(*[
                executor.execute(task)
                for task in ready
            ])

        return task_manager.get_final_result()

# 优势:
# ✓ 专业化（每个 Agent 做擅长的事）
# ✓ 并发（独立任务同时执行）
# ✓ 依赖管理（自动按顺序执行）
# ✓ 进度追踪（知道每个任务状态）
# ✓ 动态调整（可以中途添加/修改任务）
```

### 任务管理器的核心价值

#### 1. **依赖关系管理**

```python
# 没有任务管理器
# ❌ 手动管理依赖，容易出错
result1 = await agent1.process("任务1")
result2 = await agent2.process(f"任务2，基于 {result1}")  # 手动传递

# 有任务管理器
# ✓ 自动处理依赖
tasks = [
    Task(id="t1", agent="Agent1", description="任务1", dependencies=[]),
    Task(id="t2", agent="Agent2", description="任务2", dependencies=["t1"])
]
task_manager.create_tasks(tasks)

# 执行时自动:
# 1. 先执行 t1
# 2. t1 完成后，自动将结果作为上下文传给 t2
# 3. 执行 t2
```

#### 2. **并发执行**

```python
# 任务依赖图
#       t1 (研究主题A)
#      /  \
#    t2   t3  (t2 和 t3 可以并发)
#      \  /
#       t4  (等待 t2 和 t3 完成)

# 任务管理器自动识别:
ready = task_manager.get_ready_tasks()
# Round 1: [t1]
# Round 2: [t2, t3]  # 并发执行！
# Round 3: [t4]

# 手动实现会非常复杂
```

#### 3. **状态追踪**

```python
# 任何时候都知道系统状态
task_manager.get_summary()

# 输出:
# ✅ t1: [ResearchAgent] 研究主题A (completed)
# 🔄 t2: [CoderAgent] 编写代码 (executing)
# ⏳ t3: [AnalystAgent] 分析数据 (pending)
# ⏳ t4: [SummarizerAgent] 生成报告 (pending, depends on t2, t3)
```

#### 4. **错误处理和恢复**

```python
# 任务失败不影响整个系统
try:
    await executor.execute_task(task2)
except Exception as e:
    task_manager.mark_failed(task2.id, str(e))

    # Planner 可以决定:
    # - 重试 task2
    # - 修改 task2 描述
    # - 创建新任务替代
    # - 继续执行其他不依赖 task2 的任务
```

#### 5. **动态调整**

```python
# 执行过程中发现需要额外任务
# Planner 审查 t1 的结果后:
if result_insufficient:
    task_manager.add_task(
        task_id="t1.5",
        agent="ResearchAgent",
        description="深入研究特定方面",
        dependencies=["t1"]
    )
    # 其他任务自动依赖 t1.5
```

### 最小可行系统的三个组件关系

```python
# ===============================
# 1. 任务管理器 (TaskManager)
# ===============================
class TaskManager:
    """
    角色: 数据管理员
    类比: 项目看板（Trello, Jira）

    职责:
    - 存储任务数据
    - 维护任务状态
    - 计算依赖关系
    - 提供查询接口
    """

    def __init__(self):
        self.tasks = {}

    def add_task(self, task):
        self.tasks[task.id] = task

    def get_ready_tasks(self):
        """返回所有依赖已满足的任务"""
        return [
            task for task in self.tasks.values()
            if task.status == 'pending'
            and all(self.tasks[dep_id].status == 'completed'
                    for dep_id in task.dependencies)
        ]

    def mark_completed(self, task_id, result):
        self.tasks[task_id].status = 'completed'
        self.tasks[task_id].result = result


# ===============================
# 2. 简单 Agent
# ===============================
class SimpleAgent:
    """
    角色: 专业工作者
    类比: 工程师、设计师

    职责:
    - 接收任务描述
    - 调用 LLM 和工具
    - 返回执行结果
    """

    def __init__(self, name, role):
        self.name = name
        self.role = role

    async def execute(self, task_description, context=""):
        """
        执行单个任务

        Args:
            task_description: 任务描述
            context: 上下文（依赖任务的结果）

        Returns:
            执行结果
        """
        # 组合 prompt
        full_prompt = f"""
你是 {self.role}。

任务: {task_description}

上下文:
{context}

请完成任务并返回结果。
"""
        # 调用 LLM（简化）
        result = await call_llm(full_prompt)
        return result


# ===============================
# 3. 协调器 (Orchestrator)
# ===============================
class Orchestrator:
    """
    角色: 项目经理
    类比: 团队负责人

    职责:
    - 注册 Agents
    - 创建任务计划
    - 调度任务执行
    - 管理整体流程
    """

    def __init__(self):
        self.task_manager = TaskManager()
        self.agents = {}

    def register_agent(self, agent):
        """注册 Agent"""
        self.agents[agent.name] = agent

    async def run(self, user_request):
        """运行完整流程"""

        # === 步骤 1: 规划 ===
        # （简化版：手动创建任务）
        # （完整版：用 Planner Agent 自动规划）
        tasks = self._create_plan(user_request)
        for task in tasks:
            self.task_manager.add_task(task)

        # === 步骤 2: 执行 ===
        while True:
            # 获取可执行任务
            ready_tasks = self.task_manager.get_ready_tasks()

            if not ready_tasks:
                break  # 全部完成

            # 并发执行
            results = await asyncio.gather(*[
                self._execute_task(task)
                for task in ready_tasks
            ])

        # === 步骤 3: 返回结果 ===
        return self._format_final_result()

    async def _execute_task(self, task):
        """执行单个任务"""

        # 1. 找到负责的 Agent
        agent = self.agents[task.agent_name]

        # 2. 准备上下文（依赖任务的结果）
        context = ""
        for dep_id in task.dependencies:
            dep_task = self.task_manager.tasks[dep_id]
            context += f"\n[{dep_id}]: {dep_task.result}\n"

        # 3. 执行
        result = await agent.execute(task.description, context)

        # 4. 标记完成
        self.task_manager.mark_completed(task.id, result)

        return result


# ===============================
# 使用示例
# ===============================
async def main():
    # 1. 创建协调器
    orchestrator = Orchestrator()

    # 2. 注册 Agents
    orchestrator.register_agent(SimpleAgent("ResearchAgent", "研究专家"))
    orchestrator.register_agent(SimpleAgent("CoderAgent", "程序员"))

    # 3. 执行
    result = await orchestrator.run("研究 Python 并写示例代码")

    print(result)
```

### 三者的关系图

```
┌──────────────────────────────────────────────────────────┐
│                    Orchestrator                          │
│                    (协调器)                              │
│                                                          │
│  职责:                                                   │
│  • 整体流程控制                                          │
│  • 连接 TaskManager 和 Agents                          │
│  • 决定何时执行、执行什么                                │
│                                                          │
│  ┌────────────────┐              ┌─────────────────┐   │
│  │  TaskManager   │              │     Agents      │   │
│  │  (任务管理器)  │              │   (执行者)      │   │
│  │                │              │                 │   │
│  │  存储:         │              │  ResearchAgent  │   │
│  │  • 任务列表    │   Orchestrator│  CoderAgent     │   │
│  │  • 依赖关系    │◄────查询─────┤  AnalystAgent   │   │
│  │  • 任务状态    │              │  ...            │   │
│  │                │   Orchestrator│                 │   │
│  │  提供:         │─────调用────►│  执行具体任务    │   │
│  │  • 查询接口    │              │                 │   │
│  │  • 状态更新    │              │                 │   │
│  └────────────────┘              └─────────────────┘   │
│         ↑                                 ↓              │
│         │                                 │              │
│         └────── 更新状态 ←────── 返回结果 ──┘             │
└──────────────────────────────────────────────────────────┘

数据流:
1. Orchestrator 从 TaskManager 查询可执行任务
2. Orchestrator 调用对应的 Agent 执行
3. Agent 返回结果给 Orchestrator
4. Orchestrator 更新 TaskManager 的任务状态
5. 重复 1-4，直到所有任务完成
```

### 为什么需要这三个组件？

#### 如果没有 TaskManager：

```python
# ❌ Orchestrator 需要自己管理一切
class Orchestrator:
    def __init__(self):
        self.tasks = []  # 手动管理任务
        self.completed = set()  # 手动追踪完成状态
        self.results = {}  # 手动存储结果

    async def run(self, user_request):
        # 复杂的依赖计算逻辑
        for task in self.tasks:
            if all(dep in self.completed for dep in task.deps):
                # 手动准备上下文
                context = "\n".join(
                    self.results[dep] for dep in task.deps
                )
                # 执行...
                # 更新状态...

# 代码混乱，职责不清
```

#### 如果没有 Agents：

```python
# ❌ Orchestrator 需要包含所有执行逻辑
class Orchestrator:
    async def run(self, user_request):
        # 所有执行逻辑都在这里
        if "研究" in user_request:
            # 研究逻辑
            pass
        elif "编码" in user_request:
            # 编码逻辑
            pass

# 无法扩展，无法复用
```

#### 如果没有 Orchestrator：

```python
# ❌ 需要手动连接 TaskManager 和 Agents
task_manager = TaskManager()
research_agent = ResearchAgent()
coder_agent = CoderAgent()

# 手动调度
while True:
    ready = task_manager.get_ready_tasks()
    for task in ready:
        if task.agent == "ResearchAgent":
            result = await research_agent.execute(task.description)
        elif task.agent == "CoderAgent":
            result = await coder_agent.execute(task.description)
        task_manager.mark_completed(task.id, result)

# 到处都是这种逻辑，难以维护
```

---

## 问题 4: 为什么需要 BaseAgent？

### 基类的作用

#### 1. **代码复用**

```python
# === 没有基类 ===
# ❌ 每个 Agent 都要重复实现相同逻辑

class ResearchAgent:
    def __init__(self):
        self.llm_client = LLMClient()  # 重复
        self.system_prompt = "..."

    async def process(self, prompt):
        # 复杂的 ReAct Loop 逻辑
        messages = [...]
        while True:
            response = await self.llm_client.chat(...)
            # 处理 tool calls
            # 判断是否结束
            # ...
        # 这段逻辑每个 Agent 都要写一遍！

class CoderAgent:
    def __init__(self):
        self.llm_client = LLMClient()  # 重复
        self.system_prompt = "..."

    async def process(self, prompt):
        # 又要写一遍相同的 ReAct Loop！
        messages = [...]
        while True:
            # ...


# === 有基类 ===
# ✅ 通用逻辑写一次，所有子类共享

class BaseAgent:
    """所有 Agent 的基类"""

    def __init__(self, system_prompt, allowed_servers):
        self.system_prompt = system_prompt
        self.allowed_servers = allowed_servers
        self.llm_client = LLMClient()

    async def process(self, prompt):
        """
        通用的 ReAct Loop 实现
        所有子类自动继承这个逻辑
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]

        round_count = 0
        max_rounds = 20

        while round_count < max_rounds:
            round_count += 1

            # 调用 LLM
            response = await self.llm_client.chat(
                messages,
                allowed_servers=self.allowed_servers
            )

            messages.extend(response)
            last_message = messages[-1]

            # 检查是否结束
            if last_message.get("role") == "assistant" and "tool_calls" not in last_message:
                return last_message.get("content", "")

        return "Max rounds reached"


# === 子类只需要定义差异 ===

class ResearchAgent(BaseAgent):
    """研究 Agent"""

    def __init__(self):
        super().__init__(
            system_prompt="你是研究专家...",
            allowed_servers=[("browsermcp", ...)]
        )
        # 不需要实现 process()，自动继承


class CoderAgent(BaseAgent):
    """编码 Agent"""

    def __init__(self):
        super().__init__(
            system_prompt="你是程序员...",
            allowed_servers=[("file_writer", ...)]
        )
        # 不需要实现 process()，自动继承
```

#### 2. **统一接口**

```python
# Orchestrator 可以统一处理所有 Agent

class Orchestrator:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        #                    ↑
        #                 类型注解：所有 Agent 都是 BaseAgent

    def register_agent(self, agent: BaseAgent):
        """接受任何继承自 BaseAgent 的 Agent"""
        self.agents[agent.name] = agent

    async def execute_task(self, task):
        # 统一调用 process 方法
        agent = self.agents[task.agent_name]
        result = await agent.process(task.description)
        #                    ↑
        #                 所有 Agent 都有这个方法
        return result


# 添加新 Agent 不需要修改 Orchestrator
class TranslatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(...)

orchestrator.register_agent(TranslatorAgent())
# 自动工作！
```

#### 3. **强制规范**

```python
# 基类定义了 Agent 的"合约"

class BaseAgent(ABC):  # Abstract Base Class
    """
    所有 Agent 必须遵守的规范:
    1. 必须有 system_prompt
    2. 必须有 allowed_servers
    3. 必须实现 process() 方法（或使用默认实现）
    """

    @abstractmethod
    def __init__(self, system_prompt: str, allowed_servers: list):
        """子类必须调用 super().__init__()"""
        pass

    async def process(self, prompt: str) -> str:
        """所有 Agent 都必须有这个方法"""
        pass


# ❌ 错误示例：不遵守规范
class BadAgent:  # 没有继承 BaseAgent
    def do_something(self, text):  # 方法名错误
        pass

# Orchestrator 无法使用这个 Agent
agent = BadAgent()
await agent.process("...")  # AttributeError!


# ✅ 正确示例：遵守规范
class GoodAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="...",
            allowed_servers=[...]
        )

# 保证能正常工作
```

#### 4. **便于扩展和维护**

```python
# === 场景 1: 添加新功能 ===

# 需求: 所有 Agent 都要支持流式输出

class BaseAgent:
    # 只需要在基类添加一次
    async def process_stream(self, prompt: str):
        """新功能：流式处理"""
        async for chunk in self.llm_client.chat_stream(...):
            yield chunk

# 所有子类自动获得这个功能
await research_agent.process_stream("...")
await coder_agent.process_stream("...")


# === 场景 2: 修复 Bug ===

# 发现: process() 方法有内存泄漏

class BaseAgent:
    async def process(self, prompt: str) -> str:
        # 修复一次，所有 Agent 都修复了
        messages = [...]
        try:
            # ...
        finally:
            # 清理资源
            pass


# === 场景 3: 添加通用功能 ===

class BaseAgent:
    def __init__(self, ...):
        # ...
        self.cache = {}  # 添加缓存

    async def process(self, prompt: str) -> str:
        # 检查缓存
        if prompt in self.cache:
            return self.cache[prompt]

        # 执行
        result = await self._process_impl(prompt)

        # 缓存结果
        self.cache[prompt] = result
        return result

# 所有 Agent 自动获得缓存功能
```

#### 5. **类型安全**

```python
from typing import Dict

class Orchestrator:
    def __init__(self):
        # 明确类型，IDE 可以提供智能提示
        self.agents: Dict[str, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent):
        """
        类型检查:
        - ✓ 可以传入 ResearchAgent
        - ✓ 可以传入 CoderAgent
        - ✗ 不能传入 str 或其他类型
        """
        self.agents[agent.name] = agent

    async def execute_task(self, task):
        agent = self.agents[task.agent_name]
        # IDE 知道 agent 是 BaseAgent
        # 可以自动补全 .process() 方法
        result = await agent.process(task.description)
        return result
```

### BaseAgent 的具体实现

```python
# agents/base_agent.py

class BaseAgent:
    """
    所有 Agent 的基类

    提供:
    1. 通用初始化逻辑
    2. ReAct Loop 实现
    3. 统一的接口
    """

    def __init__(self, system_prompt: str, allowed_servers: list, model: str = None):
        """
        Args:
            system_prompt: Agent 的角色定义
            allowed_servers: 可用的工具服务器
            model: 使用的 LLM 模型
        """
        self.system_prompt = system_prompt
        self.allowed_servers = allowed_servers
        self.agent_name = self.__class__.__name__

        # 创建 LLM 客户端
        self.llm_client = LLMClient(model=model)

    def set_mcp_client(self, mcp_client):
        """
        设置 MCP 客户端（由 Orchestrator 调用）

        这是一个 hook 方法，允许在初始化后注入依赖
        """
        self.llm_client.set_mcp_client(mcp_client)

    async def chat(self, messages: list) -> dict:
        """
        与 Agent 对话（内部方法）

        实现 ReAct Loop:
        1. 发送消息给 LLM
        2. LLM 可能调用工具
        3. 获取工具结果
        4. 继续对话
        5. 直到 LLM 返回最终答案
        """
        # 添加 system prompt
        full_messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        full_messages.extend(messages)

        round_count = 0
        max_rounds = 20  # 防止无限循环

        while round_count < max_rounds:
            round_count += 1

            # 调用 LLM
            response_messages = await self.llm_client.chat(
                full_messages,
                allowed_servers=self.allowed_servers
            )

            # 添加响应到历史
            full_messages.extend(response_messages)

            # 检查最后一条消息
            last_message = full_messages[-1]

            # 如果是 assistant 消息且没有 tool_calls，说明完成了
            if last_message.get("role") == "assistant" and "tool_calls" not in last_message:
                return last_message

        # 达到最大轮数
        return full_messages[-1] if full_messages else {"role": "assistant", "content": "Error: No response"}

    async def process(self, prompt: str) -> str:
        """
        处理任务（公开接口）

        这是 Orchestrator 调用的方法

        Args:
            prompt: 任务描述

        Returns:
            执行结果
        """
        # 将 prompt 转换为消息格式
        messages = [{"role": "user", "content": prompt}]

        # 调用内部 chat 方法
        response = await self.chat(messages)

        # 提取文本内容
        content = response.get("content", "")

        return content


# === 子类示例 ===

class ResearchAgent(BaseAgent):
    """研究 Agent - 只需要定义差异部分"""

    def __init__(self):
        # 调用父类构造函数
        super().__init__(
            system_prompt="""
你是专业的研究助手。
你的任务是搜索和分析网络信息，生成结构化报告。

可用工具:
- navigate(url): 访问网页
- search(query): 搜索
- extract_content(): 提取页面内容

请使用工具收集信息，然后生成报告。
""",
            allowed_servers=[
                ("browsermcp", {"command": "npx", "args": ["@browsermcp/mcp@latest"]})
            ],
            model="deepseek-chat"
        )

    # 不需要重写 process() 或 chat()
    # 自动继承父类的实现


class CoderAgent(BaseAgent):
    """编码 Agent"""

    def __init__(self):
        super().__init__(
            system_prompt="""
你是专业的程序员。
创建高质量的代码文件。

可用工具:
- write_file(path, content): 写入文件
- read_file(path): 读取文件

请生成代码并保存到文件。
""",
            allowed_servers=[
                ("file_writer", str(Path(__file__).parent.parent / "tools" / "file_writer_server.py"))
            ],
            model="deepseek-chat"
        )
```

### 什么时候需要重写基类方法？

```python
# === 场景 1: 需要自定义行为 ===

class SpecialAgent(BaseAgent):
    """特殊 Agent，需要自定义处理逻辑"""

    async def process(self, prompt: str) -> str:
        """重写 process 方法"""

        # 前处理
        prompt = self.preprocess(prompt)

        # 调用父类的实现
        result = await super().process(prompt)

        # 后处理
        result = self.postprocess(result)

        return result

    def preprocess(self, prompt):
        """自定义前处理"""
        return f"[SPECIAL MODE] {prompt}"

    def postprocess(self, result):
        """自定义后处理"""
        return result.upper()


# === 场景 2: 添加额外方法 ===

class AdvancedAgent(BaseAgent):
    """高级 Agent，有额外功能"""

    async def process_batch(self, prompts: list) -> list:
        """批量处理（新方法）"""
        results = []
        for prompt in prompts:
            result = await self.process(prompt)  # 使用继承的方法
            results.append(result)
        return results

    async def validate_result(self, result: str) -> bool:
        """验证结果（新方法）"""
        # 自定义验证逻辑
        return len(result) > 100
```

### 总结：BaseAgent 的价值

```python
1. 代码复用
   ✓ ReAct Loop 写一次
   ✓ LLM 调用逻辑写一次
   ✓ 错误处理写一次

2. 统一接口
   ✓ 所有 Agent 都有 process() 方法
   ✓ Orchestrator 可以统一调用
   ✓ 类型安全

3. 易于扩展
   ✓ 添加新 Agent 只需继承
   ✓ 只需要定义差异部分
   ✓ 自动获得通用功能

4. 易于维护
   ✓ 修复 bug 只需改一处
   ✓ 添加功能自动应用到所有 Agent
   ✓ 代码组织清晰

5. 强制规范
   ✓ 确保所有 Agent 遵守相同规范
   ✓ 防止接口不一致
   ✓ 提高代码质量
```

---

## 总结

### 核心架构原则

1. **分层设计**
   - Orchestration Layer（Planner）
   - Execution Layer（Executor + TaskManager）
   - Agent Layer（Sub Agents）
   - Tool Layer（MCP）

2. **单一职责**
   - 每个组件只做一件事
   - Planner 负责规划，不执行
   - Executor 负责调度，不规划
   - Agent 负责执行，不调度

3. **低耦合高内聚**
   - 组件通过接口交互
   - 修改一个组件不影响其他组件
   - 相关功能聚合在一起

4. **可扩展性**
   - 通过继承添加新 Agent
   - 通过 MCP 添加新工具
   - 通过配置添加新功能

### 关键理解

```python
# Planner Agent
- 是主 Agent，有上帝视角
- 负责规划和调度
- 使用 task_manager 工具

# Core 文件夹
- task_manager.py: 数据层，管理任务
- executor.py: 执行层，调度 Agent
- llm_client.py: 通信层，封装 LLM API
- mcp_*.py: 工具层，工具调用基础设施

# 任务管理器
- 不是 Session，是 Session 中的子任务
- 管理依赖关系
- 支持并发执行
- 追踪状态

# BaseAgent
- 提供通用功能（ReAct Loop）
- 统一接口
- 代码复用
- 易于扩展
```

这个架构设计经过深思熟虑，每个组件都有明确的职责，整体形成一个灵活、可扩展、易维护的系统。

希望这个深度解析能帮你完全理解 multi-agent 系统的设计理念！
