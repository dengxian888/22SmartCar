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

## 3. 设计问答与集成说明

Q1: 收到 PAUSE 时导航应该怎么处理？
A: 导航必须是原子级挂起。状态机进入 PAUSED 状态，当前节点挂起，待 RESUME 后从断点继续，不能直接 Cancel 掉当前路径。

Q2: STOP 与 PENALTY 的区别？
A: STOP 表示比赛彻底结束，车辆应立刻停止并终止任务；PENALTY 表示犯规，比赛继续，但系统会记录该次犯规并计入处罚时间，下发减速等降级指令。

Q3: 物理按键和界面按钮要不要走同一条命令通道？
A: 必须走同一条命令通道。本系统底层设计了 execute_command() 统一总线，Web 按钮和外部 /api/physical_trigger 接口最终都会调用同一套逻辑，确保行为一致且都被审计日志记录。

Q4: 热切怎么验证没有重启节点？
A: 在启动 perception_node 时终端会打印 PID，热切前后终端不退出、PID 不改变，且底层模型已切换成功，以此证明没有重启节点。

## 4. 功能验收点
    多层急停：点击界面红色按钮，触发指令层发零速、话题层发 LOCK、日志层记录（不自动恢复）。

    热切换：在输入框输入新模型路径并点击，感知节点不重启并加载成功；若输入非法路径（如含 bad），则触发自动回滚。

    审计日志：所有操作生成 audit_log_YYYYMMDD.jsonl，支持 python3 tools/verify_audit.py audit_log_*.jsonl 进行防篡改校验。
