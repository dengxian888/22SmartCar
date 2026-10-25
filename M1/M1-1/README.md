编译：在工作空间根目录M1-1下执行colcon build
         然后刷新环境变量 source install/setup.bash
         
运行：1.先刷新环境变量
     2.ros2 run py01 Node_B 先挂起节点B
     3.在另外两个终端分别运行ros2 run py01 Node_C_server和ros2 run py01 Node_C_client 挂起节点C的服务端和客户端
     4.在开一个新终端，运行ros2 run py01 Node_A 节点A开始运行
     5.ctrl+c结束节点的运行
     
验证：1.查看默认参数：ros2 param get /Node_B alpha
      2. 可选，对节点B的参数进行动态调节：ros2 param set /Node_B alpha 0.9
      3.验证服务端是否运行：ros2 service call /trigger_alarm sensor_interfaces/srv/TriggerAlarm "{}"
      4.验证服务超时处理:在运行节点C服务端的窗口ctrl+c，观察当节点B输出距离小于0.3时节点C客户端终端是否打印超时
