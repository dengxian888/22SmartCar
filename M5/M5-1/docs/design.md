# M5-1 状态机引擎设计说明

## 1. 状态图 (State Diagram)
graph TD
    Start(开始步骤) --> Exec[执行 execute()]
    Exec -->|返回 SUCCESS| Done[记录成功]
    Exec -->|返回 FAILED| CheckBudget{重试预算>0?}
    CheckBudget -->|是| Sleep(等待) --> Exec
    CheckBudget -->|否| CheckFallback{存在 fallback?}
    CheckFallback -->|是| ExecFallback[递归执行 fallback 节点]
    ExecFallback -->|成功| Done
    ExecFallback -->|失败| OnFail{on_fail 策略}
    CheckFallback -->|否| OnFail
    OnFail -->|abort| Fail[整机 FAILED]
    OnFail -->|skip| Skip[记录 SKIPPED 并 degraded=True]
    
## 2.  核心取舍 (Trade-offs)

    重试预算隔离：每个节点拥有独立的 retry_budget，防止上游节点把重试次数耗尽，导致下游无法重试。

    fallback 去重：使用 self.executed 集合记录已执行节点，防止 A 触发 fallback 执行了 B，后续主流程又执行一遍 B。

    线程级协作取消：超时控制采用守护线程 join(timeout) 触发 cancel()，避免 Python 强行杀线程导致的死锁。
