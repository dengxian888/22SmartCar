# M5-1 状态机引擎设计说明

## 1. 状态流转图 (State Diagram)
graph TD
    Start(开始步骤) --> Exec[执行 execute()]
    Exec -->|返回 SUCCESS| Done[记录成功, 进入下一步]
    Exec -->|返回 FAILED| CheckBudget{重试预算>0?}
    CheckBudget -->|是| Sleep(等待 retry_interval) --> Exec
    CheckBudget -->|否| CheckFallback{存在 fallback?}
    CheckFallback -->|是| ExecFallback[递归执行 fallback 节点]
    ExecFallback -->|成功| Done
    ExecFallback -->|失败| OnFail{on_fail 策略}
    CheckFallback -->|否| OnFail
    OnFail -->|abort| Fail[整机 FAILED]
    OnFail -->|skip| Skip[记录 SKIPPED 并 degraded=True]
    
## 2. 核心设计取舍 (Trade-offs)

    重试预算隔离：每个节点拥有独立的 retry_budget，防止上游节点把重试次数耗尽，导致下游无法重试。

    防循环降级：使用 visited 集合记录降级链路，且禁止 fallback 指向自身，避免 A -> B -> A 的死循环。

    防止降级重复执行：使用 self.executed 集合记录已执行节点，若 A 失败降级去执行了 B，主流程走到 B 时会自动跳过，防止重复执行。

    协作式超时取消：使用守护线程 join(timeout) 进行步骤级超时控制。超时后触发 cancel() 设置标志位，节点内部轮询该标志位主动退出，避免 Python 强杀线程导致的死锁。

    多层级超时：不仅支持单步的 timeout，还支持通过 TaskContext.deadline 实现全局任务时限截断（返回 TIMEOUT）。
