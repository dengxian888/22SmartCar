# M5-1 纯软件状态机调度框架

本项目实现了一个不依赖 BehaviorTree 库（如 py_trees）的纯 Python 任务状态机调度引擎。
内核严格控制在 200 行以内，支持 YAML 编排、重试、降级、并发、超时取消等能力，并带有完善的彩色日志与结构化报告输出。

## 环境依赖
- Python >= 3.10
- `pip install -r requirements.txt` (依赖 PyYAML 和 Pytest)

## 运行约定

# 一键运行 Demo
python3 run_task.py tasks/task_demo.yaml

# 输出
# - 终端彩色日志（状态转移、上下文更新、重试、降级、超时各用不同颜色）
# - task_report.json（包含每步耗时、结果、重试次数、最终上下文）
# - 退出码：0=全成功，非0=有失败（便于 CI/脚本判断）

#单元测试
# 运行测试（包含 17 个用例，覆盖了节点行为与框架级逻辑）
python3 -m pytest -q

#目录结构

    task_fsm/core.py：状态机调度内核（< 200 行）

    task_fsm/context.py：共享上下文，管理预算与降级标记

    task_fsm/nodes.py：5 个标准节点（含 Mock 桩实现）

    task_fsm/logger.py：五色分级日志

    task_fsm/registry.py：类型注册表

    docs/design.md：状态图与核心设计取舍

    docs/dsl.md：YAML 编排字段说明
