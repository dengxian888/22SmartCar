# M5-1 纯软件状态机任务引擎

## 运行方式
python3 run_task.py tasks/task_demo.yaml

## 测试方法
python3 -m pytest -q


---

### 第四步：终极验证

现在你在 `M5-1/` 目录下依次执行：
```bash
# 1. 跑单测
python3 -m pytest -q
# 预期：6 passed (test_fsm 里5个 + test_nodes 里1个)

# 2. 跑标准命令入口
python3 run_task.py tasks/task_demo.yaml
# 预期：终端输出彩色日志，并生成 task_report.json
