
#### 12. `docs/dsl.md` （★ 考官按此写测试 YAML）
# YAML 编排 DSL 字段说明

此文档描述了状态机引擎支持的 YAML 字段规范。考官可按照此说明编写测试用例。

## 1. 基础任务字段 (Task)
| 字段名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `name` | string | 是 | 节点名称，需在全局唯一 |
| `type` | string | 是 | 必须注册在 `NODE_REGISTRY` 中 |
| `retry` | int | 否 | 失败重试次数，默认 0 |
| `retry_interval`| float | 否 | 每次重试的间隔（秒），默认 0 |
| `timeout` | float | 否 | 单步执行超时时间（秒） |
| `fallback` | string | 否 | 失败后降级的节点名 |
| `on_fail` | string | 否 | 降级也失败后的策略：`abort`(默认) / `skip`(标记降级并继续) |

## 2. 并发容器字段 (Parallel)
| 字段名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `parallel` | dict | 是 | 并发分支容器 |
| `parallel.fail_policy`| string | 否 | `any_fail`(默认) / `all_must_succeed` / `any_success` |
| `parallel.branches` | list | 是 | 并发子任务列表（每个子任务支持 Task 字段） |

## 3. 标准节点列表
| Type | 说明 |
| :--- | :--- |
| `WaitForTrigger` | 等待开始信号（可配 `timeout`） |
| `NavigateTo` | 导航至目标点（必填 `pose` 字典） |
| `DetectTarget` | 检测目标（可选 `min_confidence`） |
| `ExecuteGrasp` | 执行抓取 |
| `SpeakTTS` | 语音播报（必填 `text` 字符串） |

## 4. 测试桩字段 (Mock 专用)
为了支持无硬件环境下的单测与演示，节点内部预留了以下可选字段：
- `_mock`: `"fail"`（强制失败）或 `["fail", "fail", "success"]`（按顺序消费的数组）
- `_mock_trigger_after`: float，用于 `WaitForTrigger` 延迟指定秒数后成功
- `_mock_sleep`: float，用于模拟执行耗时（可被 timeout 打断）
