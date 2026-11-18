
#### 12. `docs/dsl.md` （★ 考官按此写测试 YAML）
```markdown
# YAML 编排 DSL 字段说明

| 字段名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `name` | string | 是 | 节点名称，全局唯一 |
| `type` | string | 是 | 必须在 `NODE_REGISTRY` 中注册 |
| `retry` | int | 否 | 失败重试次数，默认 0 |
| `retry_interval` | float | 否 | 每次重试间隔（秒），默认 0 |
| `timeout` | float | 否 | 单步执行超时时间（秒） |
| `fallback` | string | 否 | 失败后降级的节点名 |
| `on_fail` | string | 否 | 降级也失败后的策略：`abort`(默认) / `skip` |
| `parallel` | dict | 否 | 并发分支容器 |
| `parallel.fail_policy` | string | 否 | `any_fail`(默认) / `all_must_succeed` / `any_success` |
| `parallel.branches` | list | 是 | 并发子任务列表 |

**注**：为了支持单元测试和考官验收，所有节点支持注入 `_mock`（`fail` / `success`）及 `_mock_sleep` 等测试桩字段。
