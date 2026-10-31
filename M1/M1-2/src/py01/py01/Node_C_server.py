import rclpy
from rclpy.node import Node
from sensor_interfaces.srv import TriggerAlarm

class AlarmServer(Node):
    def __init__(self):
        super().__init__('alarm_server_node')
        self.srv = self.create_service(TriggerAlarm, 'trigger_alarm', self.handle_alarm)
        
        self.get_logger().info("节点C：服务端已启动")

    def handle_alarm(self, request, response):
        self.get_logger().info('[ALARM] 距离过近！') # 题目要求的打印
        response.success = True
        response.message = "报警成功"
        return response

def main(args=None):
    rclpy.init()
    node = AlarmServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()