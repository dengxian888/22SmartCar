import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist

class EmergencyStopSub(Node):
    def __init__(self):
        super().__init__('emergency_stop_sub')
        self.sub = self.create_subscription(String, '/emergency_stop', self.callback, 10)
        # 拦截层：我们订阅原命令，再发布出去
        self.cmd_sub = self.create_subscription(Twist, '/cmd_vel_raw', self.cmd_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.locked = False

    def callback(self, msg):
        if msg.data == "LOCK":
            self.locked = True
            self.get_logger().error("⛔ 底盘硬锁死！拦截所有运动指令。")
        elif msg.data == "UNLOCK":
            self.locked = False
            self.get_logger().info("✅ 底盘锁解除。")

    def cmd_callback(self, msg):
        if self.locked:
            # 丢弃原指令，发零速
            self.cmd_pub.publish(Twist())
        else:
            self.cmd_pub.publish(msg)