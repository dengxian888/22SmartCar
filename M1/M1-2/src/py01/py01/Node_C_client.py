import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from sensor_interfaces.srv import TriggerAlarm

class AlarmClientNode(Node):
    def __init__(self):
        super().__init__('node_c_alarm')
        
        # 1. 声明参数
        self.declare_parameter('alarm_threshold', 0.3)
        self.declare_parameter('service_timeout', 1.0)
        self.threshold = self.get_parameter('alarm_threshold').value
        self.timeout = self.get_parameter('service_timeout').value

        # 2. 订阅距离数据
        self.subscription = self.create_subscription(
            Float32, 'processed_distance', self.distance_callback, 10)

        # 3. 创建服务客户端（只负责发请求）
        self.cli = self.create_client(TriggerAlarm, 'trigger_alarm')
        
        # 4. 状态管理
        self.pending_future = None
        self.start_time = None
        
        # 5. 超时检测定时器（0.1秒检查一次）
        self.timeout_timer = self.create_timer(0.1, self.check_timeout)
        
        self.get_logger().info("节点C：客户端已启动")

    def distance_callback(self, msg):
        # 如果距离过近，且当前没有正在等待的请求
        if msg.data < self.threshold and self.pending_future is None:
            self.get_logger().info(f"距离 {msg.data:.2f}m < {self.threshold}m，触发报警请求！")
            
            # 发起异步请求
            req = TriggerAlarm.Request()
            self.pending_future = self.cli.call_async(req)
            
            # 绑定响应回调
            self.pending_future.add_done_callback(self.response_callback)
            
            # 记录时间
            self.start_time = self.get_clock().now()

    def response_callback(self, future):
        # 如果已经超时被抛弃了，就不再处理
        if self.pending_future is None:
            return
            
        try:
            response = future.result()
            self.get_logger().info(f"服务端响应: {response.message}")
        except Exception as e:
            self.get_logger().error(f"服务调用失败: {e}")
        finally:
            # 收到响应，清空状态
            self.pending_future = None
            self.start_time = None

    def check_timeout(self):
        if self.pending_future is not None and self.start_time is not None:
            elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
            
            # 超时判断
            if elapsed > self.timeout and not self.pending_future.done():
                self.get_logger().warn('[WARN] 报警服务超时')
                # 放弃本次请求，允许下次再次触发
                self.pending_future = None
                self.start_time = None

def main(args=None):
    rclpy.init()
    node = AlarmClientNode()
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