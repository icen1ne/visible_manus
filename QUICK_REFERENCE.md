# Multi-Agent 系统快速参考

快速查阅关键概念和代码模板

---

## 🎯 核心概念速查

### 1. 四大核心组件

```
┌─────────────┐
│   Planner   │  智能规划器，制定和调整任务
└──────┬──────┘
       │
       ↓
┌─────────────┐
│TaskManager  │  任务管理器，处理依赖和状态
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Executor   │  执行器，调度 Agent 执行任务
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Agents    │  专业 Agent，完成具体任务
└─────────────┘
```

### 2. 数据流向

```
用户输入
  ↓
Planner 分析 → 创建任务列表
  ↓
TaskManager 管理任务依赖
  ↓
Executor 按依赖顺序执行
  ↓
Agent 1 执行 → 结果
  ↓
Agent 2 执行（使用 Agent 1 的结果）→ 结果
  ↓
Planner 审核 → 调整计划 或 完成
  ↓
返回最终结果
```

### 3. ReAct 循环

```
┌──────────────────────────────────┐
│  Loop until task complete:       │
│                                  │
│  1. Think (推理)                 │
│     ↓                            │
│  2. Act (执行工具/创建任务)       │
│     ↓                            │
│  3. Observe (观察结果)            │
│     ↓                            │
│  4. Back to Think                │
└──────────────────────────────────┘
```

---

## 💻 代码模板速查

### Task 数据结构

```python
@dataclass
class Task:
    task_id: str              # "t1", "t2", ...
    agent: str                # "ResearchAgent"
    description: str          # "研究 React Hooks"
    dependencies: List[str]   # ["t1"] - 依赖的任务
    status: TaskStatus        # pending/executing/completed/failed
    result: Optional[str]     # 执行结果
```

### 创建 Agent

```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="你是一个专业的...",
            allowed_servers=[("tool_server", "path/to/server.py")]
        )

    async def process(self, prompt: str) -> str:
        # Agent 的核心逻辑
        # 1. 接收任务描述
        # 2. 调用 LLM + 工具完成任务
        # 3. 返回结果
        return result
```

### 创建 MCP 工具

```python
from mcp.server.fastmcp import FastMCP

server = FastMCP("MyTool")

@server.tool()
def my_function(param: str) -> str:
    """工具描述 - LLM 会看到这个"""
    # 实现工具逻辑
    return result

if __name__ == "__main__":
    server.run()
```

### 任务管理

```python
# 创建任务列表
task_list = TaskList()
task_list.create_tasks([
    {
        "task_id": "t1",
        "agent": "ResearchAgent",
        "description": "研究主题",
        "dependencies": []
    },
    {
        "task_id": "t2",
        "agent": "CoderAgent",
        "description": "编写代码",
        "dependencies": ["t1"]  # 依赖 t1
    }
])

# 获取可执行的任务（依赖已满足）
ready = task_list.get_ready_tasks()

# 执行任务
for task in ready:
    result = await agent.process(task.description)
    task_list.mark_completed(task.task_id, result)
```

### WebSocket 事件处理

#### 后端发送事件

```python
# server.py
await emitter.broadcast('event_type', {
    'key': 'value'
})

# 常用事件类型
broadcast('planner_status', {'status': 'working'})
broadcast('tool_call', {'agent': 'Planner', 'tool': 'create_task_list'})
broadcast('tasks_update', {'tasks': [...]})
broadcast('agent_status', {'agent': 'ResearchAgent', 'status': 'working'})
broadcast('output', {'text': 'Final result', 'files': [...]})
```

#### 前端接收事件

```typescript
// useWebSocket.ts
const handleMessage = (event: MessageEvent) => {
    const { type, data } = JSON.parse(event.data);

    switch (type) {
        case 'planner_status':
            store.setPlannerStatus(data.status);
            break;
        case 'tasks_update':
            store.setTasks(data.tasks);
            break;
        // ... 更多事件
    }
};
```

---

## 📊 项目结构速查

### 最小文件结构

```
my_agent_system/
├── agents/
│   ├── base_agent.py         # Agent 基类
│   └── my_agent.py           # 自定义 Agent
├── core/
│   ├── task_manager.py       # 任务管理
│   ├── executor.py           # 执行器
│   └── llm_client.py         # LLM 客户端
├── planner/
│   └── planner_agent.py      # Planner
├── tools/
│   └── my_tool_server.py     # 工具
├── main.py                    # 入口
└── requirements.txt           # 依赖
```

### 必需依赖

```txt
# requirements.txt
openai>=2.0.0              # LLM API
python-dotenv>=1.0.0       # 环境变量
mcp>=1.0.0                 # 工具协议
fastmcp>=2.0.0             # MCP 服务器
websockets>=12.0           # WebSocket (如果需要前端)
```

---

## 🔧 常用操作速查

### 1. 初始化系统

```python
# 创建 MCP 管理器
manager = get_mcp_manager()
await manager.initialize([
    ("planner", "path/to/planner.py"),
    ("tools", "path/to/tools.py")
])

# 创建 Planner
planner_client = LLMClient()
planner_client.set_mcp_client(manager.get_client())

# 创建 Agents
agents = {
    "ResearchAgent": ResearchAgent(),
    "CoderAgent": CoderAgent()
}

# 为每个 agent 设置 MCP 客户端
for agent in agents.values():
    agent.set_mcp_client(manager.get_client())
```

### 2. 执行 ReAct 循环

```python
async def react_loop(user_request: str):
    # 初始消息
    messages = [
        {"role": "system", "content": PLANNER_PROMPT},
        {"role": "user", "content": user_request}
    ]

    while True:
        # Planner 推理
        response = await planner_client.chat(messages)
        messages.extend(response)

        last_msg = messages[-1]

        # 处理工具调用
        if last_msg.get("role") == "tool":
            content = last_msg["content"]

            if "CONTINUE" in content:
                # 执行下一批任务
                results = await executor.execute_ready_tasks()
                messages.append({"role": "user", "content": results})

            elif "FINALIZED" in content:
                # 完成
                return extract_final_response(content)
```

### 3. 并发执行任务

```python
# 获取所有就绪任务
ready_tasks = task_list.get_ready_tasks()

# 并发执行
results = await asyncio.gather(*[
    executor.execute_task(task)
    for task in ready_tasks
])
```

### 4. 错误处理

```python
try:
    result = await agent.process(task.description)
    task_list.mark_completed(task.task_id, result)
except Exception as e:
    task_list.mark_failed(task.task_id, str(e))
    # 通知 Planner 调整计划
    await notify_planner_of_failure(task.task_id, str(e))
```

---

## 🎨 前端状态管理速查

### Zustand Store 结构

```typescript
interface SystemStore {
    // 节点状态
    inputStatus: 'idle' | 'active' | 'working' | 'complete' | 'error';
    plannerStatus: NodeStatus;
    researchAgentStatus: NodeStatus;

    // 数据
    inputText: string;
    tasks: Task[];
    messages: Message[];

    // 动作
    setInputText: (text: string) => void;
    setPlannerStatus: (status: NodeStatus) => void;
    addMessage: (msg: Message) => void;
}
```

### 使用 Store

```typescript
// 在组件中使用
const { tasks, plannerStatus } = useSystemStore();

// 更新状态
const { setPlannerStatus } = useSystemStore();
setPlannerStatus('working');
```

---

## 📝 Prompt 模板速查

### Planner Prompt 模板

```python
PLANNER_PROMPT = """
你是任务规划助手，负责将用户请求分解为可执行任务。

## 可用工具
1. create_task_list - 创建初始任务列表
2. add_task - 添加新任务
3. modify_task - 修改任务
4. continue_execution - 继续执行任务
5. finalize_plan - 完成并返回结果

## 可用 Agents
- ResearchAgent: 网络研究
- CoderAgent: 代码生成
- AnalystAgent: 数据分析

## 工作流程
1. 分析用户请求
2. 创建任务列表（使用 create_task_list）
3. 审核任务执行结果
4. 必要时调整计划
5. 所有任务完成后调用 finalize_plan
"""
```

### Agent Prompt 模板

```python
RESEARCH_AGENT_PROMPT = """
你是专业研究助手。

## 职责
- 搜索和分析网络信息
- 综合多个来源
- 生成结构化报告

## 可用工具
- web_search(query): 搜索
- browse(url): 访问网页
- extract_content(): 提取内容

## 输出格式
**摘要**: ...
**关键发现**: ...
**详细信息**: ...
**来源**: ...
"""
```

---

## 🚀 开发清单

### Phase 1: 基础功能 ✓
- [ ] 实现 TaskManager
- [ ] 创建 BaseAgent
- [ ] 实现一个简单 Agent
- [ ] 基础执行流程

### Phase 2: 工具集成 ✓
- [ ] 创建 MCP 工具服务器
- [ ] 集成工具调用到 Agent
- [ ] 测试工具调用

### Phase 3: 智能规划 ✓
- [ ] 实现 Planner Agent
- [ ] ReAct 循环
- [ ] 动态任务调整

### Phase 4: 前端可视化 ✓
- [ ] WebSocket 服务器
- [ ] React 前端
- [ ] 实时状态更新
- [ ] 可视化画布

### Phase 5: 生产级特性 ⚠
- [ ] 错误处理和重试
- [ ] 日志和监控
- [ ] 性能优化
- [ ] 安全性

---

## 🐛 调试技巧

### 1. 查看 LLM 调用

```python
# 设置 verbose 模式
VERBOSE = True

if VERBOSE:
    print(f"Calling LLM with messages: {messages}")
    print(f"Response: {response}")
```

### 2. 追踪任务状态

```python
# 打印任务摘要
print(task_list.get_summary())

# 输出:
# Task List Status:
#   ⏳ t1: [ResearchAgent] Research topic...
#   ✅ t2: [CoderAgent] Generate code...
```

### 3. 监控 WebSocket 消息

```typescript
// 在浏览器控制台
wsRef.current.addEventListener('message', (e) => {
    console.log('WS Message:', JSON.parse(e.data));
});
```

### 4. 检查依赖图

```python
def print_dependency_graph(task_list):
    for task in task_list.tasks:
        deps_str = " -> ".join(task.dependencies) if task.dependencies else "None"
        print(f"{task.task_id}: depends on {deps_str}")
```

---

## 📚 关键文件速查

### 必读文件

```
visible_manus/
├── core/task_manager.py      ⭐ 任务管理核心
├── core/executor.py           ⭐ 任务执行逻辑
├── planner/planner_agent.py   ⭐ Planner 实现
├── agents/base_agent.py       ⭐ Agent 基类
├── main.py                    ⭐ 命令行入口
├── server.py                  ⭐ WebSocket 服务器
└── frontend/src/hooks/useWebSocket.ts  ⭐ 前端通信
```

### 配置文件

```bash
# .env
DEEPSEEK_API_KEY=your_key
DEEPSEEK_URL=https://api.deepseek.com

# 或使用其他 LLM
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

---

## 🔗 有用的命令

```bash
# 运行后端（命令行模式）
python main.py

# 运行 WebSocket 服务器
python server.py

# 运行前端
cd frontend && npm run dev

# 测试简单示例
python SIMPLE_EXAMPLE.py

# 查看日志（开启详细模式）
VERBOSE=true python main.py
```

---

## 💡 最佳实践

### ✅ DO

1. **清晰的任务描述**
   ```python
   # ✅ 好
   "研究 React Hooks，重点关注 useState 和 useEffect 的用法和最佳实践"

   # ❌ 差
   "研究 React"
   ```

2. **合理的依赖关系**
   ```python
   # ✅ 好 - 清晰的依赖链
   t1: Research → t2: Code → t3: Test

   # ❌ 差 - 循环依赖
   t1 depends on t2, t2 depends on t1
   ```

3. **适当的并发**
   ```python
   # ✅ 好 - 独立任务并发
   t1: Research topic A
   t2: Research topic B  # 可以同时执行

   # ❌ 差 - 不必要的串行
   t1: Research, t2: depends on t1 (but doesn't need t1's result)
   ```

### ❌ DON'T

1. **不要过度细分任务**
   ```python
   # ❌ 差 - 太细
   t1: Open browser
   t2: Search Google
   t3: Click first link
   t4: Read content

   # ✅ 好 - 合理粒度
   t1: Research the topic using web search
   ```

2. **不要忽略错误处理**
   ```python
   # ❌ 差
   result = await agent.process(task)

   # ✅ 好
   try:
       result = await agent.process(task)
   except Exception as e:
       handle_error(e)
   ```

3. **不要在前端做重计算**
   ```typescript
   // ❌ 差 - 前端计算复杂逻辑
   const processedData = complexAlgorithm(largeDataset);

   // ✅ 好 - 后端计算，前端显示
   const { processedData } = useSystemStore();
   ```

---

**快速参考完成！** 📖

需要更多细节？查看 [TUTORIAL.md](./TUTORIAL.md)
想看代码？运行 [SIMPLE_EXAMPLE.py](./SIMPLE_EXAMPLE.py)
