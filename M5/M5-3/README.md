# M5-3 统一任务终端与安全系统

## 1. 运行环境与依赖
pip3 install flask requests
source /opt/ros/humble/setup.bash

## 2. 快速启动

为了模拟完整的比赛环境，请开启 三个终端。

终端 1：启动模拟感知节点（用于验证热切不重启）
python3 mock_perception.py

终端 2：启动统一任务终端
python3 -m host_side.operator_terminal

终端 3：启动裁判模拟器（可选，Web界面也可直接点）
python3 tools/referee_sim.py

启动后，在浏览器访问：http://127.0.0.1:8081

## 3. 功能验收点
    多层急停：点击界面红色按钮，触发指令层发零速、话题层发 LOCK、日志层记录（不自动恢复）。

    热切换：在输入框输入新模型路径并点击，感知节点不重启并加载成功；若输入非法路径（如含 bad），则触发自动回滚。

    审计日志：所有操作生成 audit_log_YYYYMMDD.jsonl，支持 python3 tools/verify_audit.py audit_log_*.jsonl 进行防篡改校验。
