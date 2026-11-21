import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from .audit import AuditLogger
import time

class RefereeBridge(Node):
    def __init__(self, audit: AuditLogger):
        super().__init__('referee_bridge')
        self.audit = audit
        self.state = "READY"
        
        self.cmd_sub = self.create_subscription(String, '/referee/cmd', self.referee_callback, 10)
        self.status_pub = self.create_publisher(String, '/referee/status', 10)
        self.timer = self.create_timer(1.0, self.publish_status)
        self.last_cmd_time = time.monotonic()
        self.watchdog_timer = self.create_timer(1.0, self._watchdog_check)
        
    def _watchdog_check(self):
        if self.state == "RUNNING" and time.monotonic() - self.last_cmd_time > 120:
            self.state = "FAULT"
            self.audit.log(op="REFEREE_TIMEOUT", source="watchdog", result="fault")
            self.get_logger().warn("裁判指令超时，自动进入 FAULT 状态")

    # 修改：增加 trigger_source 参数，默认为 "referee_topic"
    def referee_callback(self, msg, trigger_source="referee_topic"):
        self.last_cmd_time = time.monotonic()
        cmd = msg.data.upper()
        self.get_logger().info(f"📡 收到指令: {cmd} (来源: {trigger_source})")
        
        if cmd == "START":
            self.state = "RUNNING"
        elif cmd == "PAUSE":
            self.state = "PAUSED"
            self.audit.log(op="REFEREE_PAUSE", source=trigger_source, result="ok")
        elif cmd == "RESUME":
            self.state = "RUNNING"
        elif cmd == "STOP":
            self.state = "STOPPED"
        elif cmd == "PENALTY":
            self.audit.log(op="REFEREE_PENALTY", source=trigger_source, result="penalty")
        elif cmd == "SCORE_QUERY":
            self.publish_status()
        else:
            self.get_logger().warn(f"未知裁判指令: {cmd}")
            
        self.publish_status()

    def publish_status(self):
        msg = String()
        msg.data = self.state
        self.status_pub.publish(msg)