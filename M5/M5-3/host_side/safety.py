import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from .audit import AuditLogger

class SafetyLayer(Node):
    def __init__(self, audit: AuditLogger):
        super().__init__('host_safety_layer')
        self.audit = audit
        self.estop_engaged = False
        
        # 层1: 指令层（直接发零速）
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        # 层2: 话题层（通知底层订阅者锁死）
        self.estop_pub = self.create_publisher(String, '/emergency_stop', 10)
        
        # 层3: 控制器层（锁定参数/服务，视具体底盘而定，此处预留）
        # self.controller_client = ...

    def trigger_emergency_stop(self, source="web_ui", reason="manual"):
        if self.estop_engaged:
            return
        
        # ① 指令层：发零速度
        self.cmd_pub.publish(Twist()) 
        
        # ② 话题层：发急停信号
        self.estop_pub.publish(String(data="LOCK"))
        
        # ③ 控制器层：锁定
        # self._lock_controller()
        
        self.estop_engaged = True
        
        # ④ 记录层：写审计
        self.audit.log(op="EMERGENCY_STOP", source=source, result="ok", reason=reason)
        self.get_logger().error("🚨 多层急停已触发，等待手动复位！")

    def manual_reset(self, source="web_ui"):
        if not self.estop_engaged:
            return
        self.estop_pub.publish(String(data="UNLOCK"))
        self.estop_engaged = False
        self.audit.log(op="EMERGENCY_STOP_RESET", source=source, result="ok")
        self.get_logger().info("✅ 急停解除。")