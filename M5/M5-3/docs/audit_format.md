# 审计日志格式规范

日志按天切割：`audit_log_YYYYMMDD.jsonl`。为防止篡改，采用哈希链（Blockchain 思想）与外部锚点机制。
**哈希算法统一采用 SHA-256**。第一条记录的 `prev_hash` 为空字符串 `""`。

## 字段说明
| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `ts` | string | 毫秒级 ISO8601 时间戳 |
| `op` | string | 操作类型（如 E-STOP, MODEL_SWITCH） |
| `source` | string | 触发源（web_ui, referee, voice_offline, physical_button） |
| `prev_hash` | string | 上一条日志的哈希。**第一条为空字符串 `""`** |
| `hash` | string | 当前记录的 **SHA-256** 哈希值 |

## 防篡改验证方式
1. 运行 `python3 tools/verify_audit.py <log_file>`
2. 脚本会逐行重算 **SHA-256** 哈希，并与记录的 `hash` 和 `prev_hash` 比对。
3. 最后一行的 `hash` 会与 `audit_anchor_YYYYMMDD.txt` 中的外部锚点比对。
4. 如果发生中间行篡改，或者尾部截断，验证将直接报 `FAIL`。
