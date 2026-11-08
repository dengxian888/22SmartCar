import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image
from message_filters import Subscriber, ApproximateTimeSynchronizer
import statistics # Python 自带的统计库

class SyncNode(Node):
    def __init__(self):
        super().__init__('sync_node')
        
        # 1. 声明参数（带默认值）
        self.declare_parameter('slop', 0.05)      # 默认 50ms
        self.declare_parameter('queue_size', 60)  # 默认队列长度 50
        
        self.dt_list = [] # 用来存每次配对的时间差
        
        # 2. 获取参数
        slop = self.get_parameter('slop').value
        queue_size = self.get_parameter('queue_size').value
        self.get_logger().info(f'启动同步节点，slop={slop}, queue={queue_size}')

        # 3. 创建 message_filters 专用的 Subscriber
        # 注意：这里不是 self.create_subscription，而是 message_filters.Subscriber
        self.scan_sub = Subscriber(self, LaserScan, '/scan')
        self.image_sub = Subscriber(self, Image, '/camera/image_raw')

        # 4. 创建近似时间同步器
        self.ts = ApproximateTimeSynchronizer(
            [self.scan_sub, self.image_sub],
            queue_size=queue_size,
            slop=slop
        )
        # 5. 注册回调函数
        self.ts.registerCallback(self.sync_callback)

        self.match_count = 0 # 记录配对次数

    def sync_callback(self, scan_msg, image_msg):
        self.match_count += 1
        
        # 计算时间差（单位：毫秒）
        scan_t = scan_msg.header.stamp.sec + scan_msg.header.stamp.nanosec * 1e-9
        img_t = image_msg.header.stamp.sec + image_msg.header.stamp.nanosec * 1e-9
        dt_ms = abs(scan_t - img_t) * 1000.0
        self.dt_list.append(dt_ms)
        
        
        #self.get_logger().info(f'✅ 成功配对第 {self.match_count} 对！时间差: {dt_ms:.2f} ms')

def main(args=None):
    rclpy.init(args=args)
    node = SyncNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass # 按下 Ctrl+C 时静默退出
    finally:
        # 退出时，计算总数和中位数
        if node.dt_list:
            total_frames = len(node.dt_list)
            median_dt = statistics.median(node.dt_list)
            print("\n" + "="*30)
            print(f"🎯 实验统计结果")
            print(f"总配对数: {total_frames} 对")
            print(f"时间差中位数: {median_dt:.2f} ms")
            print("="*30 + "\n")
        
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()