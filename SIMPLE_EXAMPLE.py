"""
最小化 Multi-Agent 系统示例
演示核心概念，无需复杂依赖

适合学习和理解基本原理
"""

import asyncio
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


# ========== 1. 任务管理 ==========

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """任务数据结构"""
    id: str
    agent_name: str
    description: str
    dependencies: List[str]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None


class TaskManager:
    """任务管理器 - 管理任务依赖和状态"""

    def __init__(self):
        self.tasks: dict[str, Task] = {}

    def add_task(self, task: Task):
        """添加任务"""
        self.tasks[task.id] = task
        print(f"📋 Added task: {task.id} -> {task.agent_name}")

    def get_ready_tasks(self) -> List[Task]:
        """获取所有依赖已满足的待执行任务"""
        ready = []
        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue

            # 检查依赖是否都完成
            deps_satisfied = all(
                self.tasks[dep_id].status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
                if dep_id in self.tasks
            )

            if deps_satisfied:
                ready.append(task)

        return ready

    def mark_completed(self, task_id: str, result: str):
        """标记任务完成"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.COMPLETED
            self.tasks[task_id].result = result
            print(f"✅ Task {task_id} completed")

    def mark_failed(self, task_id: str, error: str):
        """标记任务失败"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.FAILED
            self.tasks[task_id].result = error
            print(f"❌ Task {task_id} failed: {error}")

    def get_context_for_task(self, task: Task) -> str:
        """获取任务的上下文（依赖任务的结果）"""
        context = ""
        for dep_id in task.dependencies:
            if dep_id in self.tasks:
                dep_task = self.tasks[dep_id]
                context += f"\n[来自任务 {dep_id} 的结果]:\n{dep_task.result}\n"
        return context


# ========== 2. Agent 基类 ==========

class BaseAgent:
    """Agent 基类"""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    async def execute(self, task_description: str, context: str = "") -> str:
        """
        执行任务

        参数:
            task_description: 任务描述
            context: 上下文（来自依赖任务的结果）

        返回:
            执行结果
        """
        raise NotImplementedError


# ========== 3. 具体 Agent 实现 ==========

class ResearchAgent(BaseAgent):
    """研究 Agent - 负责信息搜集"""

    def __init__(self):
        super().__init__("ResearchAgent", "信息研究专家")

    async def execute(self, task_description: str, context: str = "") -> str:
        print(f"\n🔍 {self.name} 开始工作...")
        print(f"   任务: {task_description}")

        # 模拟研究过程
        await asyncio.sleep(1)  # 模拟耗时操作

        # 这里应该调用 LLM API 或搜索工具
        # 为了演示，我们返回模拟结果
        result = f"""
研究报告: {task_description}

主要发现:
1. 这是一个关于 {task_description} 的研究
2. 通过分析多个来源，我们发现...
3. 关键要点包括...

结论: 研究完成
"""
        return result.strip()


class CoderAgent(BaseAgent):
    """编码 Agent - 负责代码生成"""

    def __init__(self):
        super().__init__("CoderAgent", "代码生成专家")

    async def execute(self, task_description: str, context: str = "") -> str:
        print(f"\n💻 {self.name} 开始工作...")
        print(f"   任务: {task_description}")
        if context:
            print(f"   上下文: {context[:100]}...")

        # 模拟编码过程
        await asyncio.sleep(1)

        # 这里应该调用 LLM API 生成代码
        result = f"""
已生成代码: {task_description}

基于上下文中的研究结果，生成了以下文件:
- index.html: 主页面
- style.css: 样式文件
- script.js: 交互逻辑

代码已保存到 output/ 目录
"""
        return result.strip()


class AnalystAgent(BaseAgent):
    """分析 Agent - 负责数据分析"""

    def __init__(self):
        super().__init__("AnalystAgent", "数据分析专家")

    async def execute(self, task_description: str, context: str = "") -> str:
        print(f"\n📊 {self.name} 开始工作...")
        print(f"   任务: {task_description}")

        await asyncio.sleep(1)

        result = f"""
分析报告: {task_description}

数据分析结果:
- 发现 3 个关键模式
- 性能提升 45%
- 建议采取 5 项优化措施
"""
        return result.strip()


# ========== 4. Orchestrator (协调器) ==========

class Orchestrator:
    """协调器 - 管理多个 Agent 的协作"""

    def __init__(self):
        self.task_manager = TaskManager()
        self.agents: dict[str, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent):
        """注册 Agent"""
        self.agents[agent.name] = agent
        print(f"✓ Registered agent: {agent.name} ({agent.role})")

    def create_plan(self, user_request: str) -> List[Task]:
        """
        根据用户请求创建执行计划

        在真实系统中，这里会调用 Planner Agent (LLM) 来动态生成计划
        这里我们用简单的规则来演示
        """
        print(f"\n📝 Planning for: {user_request}\n")

        # 示例: 根据关键词判断需要哪些任务
        tasks = []

        if "研究" in user_request or "调查" in user_request:
            tasks.append(Task(
                id="task1",
                agent_name="ResearchAgent",
                description=f"研究: {user_request}",
                dependencies=[]
            ))

        if "代码" in user_request or "网页" in user_request or "程序" in user_request:
            # 如果有研究任务，编码任务依赖它
            deps = ["task1"] if tasks else []
            tasks.append(Task(
                id="task2",
                agent_name="CoderAgent",
                description=f"编写代码: {user_request}",
                dependencies=deps
            ))

        if "分析" in user_request:
            tasks.append(Task(
                id="task3",
                agent_name="AnalystAgent",
                description=f"数据分析: {user_request}",
                dependencies=[]
            ))

        # 如果没有匹配到，创建一个默认研究任务
        if not tasks:
            tasks.append(Task(
                id="task1",
                agent_name="ResearchAgent",
                description=user_request,
                dependencies=[]
            ))

        return tasks

    async def execute_task(self, task: Task) -> str:
        """执行单个任务"""
        print(f"\n▶️  Executing task: {task.id}")

        agent = self.agents.get(task.agent_name)
        if not agent:
            raise ValueError(f"Agent {task.agent_name} not found")

        # 获取依赖任务的结果作为上下文
        context = self.task_manager.get_context_for_task(task)

        # 执行任务
        try:
            task.status = TaskStatus.RUNNING
            result = await agent.execute(task.description, context)
            self.task_manager.mark_completed(task.id, result)
            return result
        except Exception as e:
            self.task_manager.mark_failed(task.id, str(e))
            raise

    async def run(self, user_request: str):
        """运行完整的协调流程"""
        print("=" * 70)
        print("🚀 Multi-Agent System Started")
        print("=" * 70)

        # 1. 创建计划
        tasks = self.create_plan(user_request)

        # 2. 添加所有任务到任务管理器
        for task in tasks:
            self.task_manager.add_task(task)

        print(f"\n📋 Created {len(tasks)} tasks")
        print("─" * 70)

        # 3. 执行任务（处理依赖关系）
        while True:
            # 获取可以执行的任务
            ready_tasks = self.task_manager.get_ready_tasks()

            if not ready_tasks:
                # 检查是否所有任务都完成了
                all_completed = all(
                    task.status == TaskStatus.COMPLETED
                    for task in self.task_manager.tasks.values()
                )
                if all_completed:
                    break
                else:
                    # 有任务失败或还在等待
                    print("\n⚠️  No more tasks can be executed")
                    break

            print(f"\n⏳ Found {len(ready_tasks)} ready tasks")

            # 并发执行所有就绪的任务
            await asyncio.gather(*[
                self.execute_task(task)
                for task in ready_tasks
            ])

        # 4. 总结结果
        print("\n" + "=" * 70)
        print("🎉 Execution Complete")
        print("=" * 70)

        print("\n📊 Summary:")
        for task in self.task_manager.tasks.values():
            status_icon = "✅" if task.status == TaskStatus.COMPLETED else "❌"
            print(f"{status_icon} {task.id}: {task.status.value}")
            if task.result:
                result_preview = task.result[:100] + "..." if len(task.result) > 100 else task.result
                print(f"   Result: {result_preview}\n")


# ========== 5. 主程序 ==========

async def main():
    """主函数 - 演示系统运行"""

    # 创建协调器
    orchestrator = Orchestrator()

    # 注册 Agents
    orchestrator.register_agent(ResearchAgent())
    orchestrator.register_agent(CoderAgent())
    orchestrator.register_agent(AnalystAgent())

    print("\n" + "=" * 70)
    print("System Ready")
    print("=" * 70)

    # 示例 1: 研究 + 编码
    print("\n\n" + "▶" * 30 + " Example 1 " + "▶" * 30)
    await orchestrator.run("研究 React Hooks 并编写示例代码")

    # 重置任务管理器
    orchestrator.task_manager = TaskManager()

    # 示例 2: 纯研究
    print("\n\n" + "▶" * 30 + " Example 2 " + "▶" * 30)
    await orchestrator.run("研究人工智能的最新趋势")

    # 示例 3: 编码任务
    orchestrator.task_manager = TaskManager()
    print("\n\n" + "▶" * 30 + " Example 3 " + "▶" * 30)
    await orchestrator.run("创建一个响应式网页")


# ========== 6. 运行 ==========

if __name__ == "__main__":
    """
    运行方式:
        python SIMPLE_EXAMPLE.py

    这个示例展示了:
    1. 任务管理和依赖关系
    2. 多个专业 Agent
    3. 并发执行
    4. 上下文传递

    在真实系统中，你需要:
    1. 集成真实的 LLM API (OpenAI, Anthropic, Google, etc.)
    2. 添加工具调用能力 (MCP, Function Calling)
    3. 实现更智能的 Planner (使用 LLM 动态规划)
    4. 添加错误处理和重试逻辑
    5. 集成 WebSocket 实现实时前端更新
    """
    asyncio.run(main())
