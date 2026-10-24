import rclpy
from rclpy.node import Node
from sensor_interfaces.msg import SensorData
import random

class Talker(Node):
    def __init__(self):
        super().__init__("talker_node_py")
        self.get_logger().info("发布方创建")
        self.publisher=self.create_publisher(SensorData,"/sensor_data",10)
        
        self.timer=self.create_timer(0.1,self.on_timer)
        
    def on_timer(self):
        message=SensorData()
        
        message.distance = float(random.uniform(0.0, 5.0))
        message.unit = "m"
        message.stamp = self.get_clock().now().to_msg()
        # 模拟状态：90%正常，5%超量程，5%错误
        rand_val = random.random()
        if rand_val > 0.95:
            message.status = 2  # 传感器错误
        elif rand_val > 0.90:
            message.status = 1  # 超出量程
        else:
            message.status = 0  # 正常
            
        self.publisher.publish(message)
        self.get_logger().info(f'发布: 距离={message.distance:.2f}{message.unit}, 时间={message.stamp},状态={message.status}')
        
        

def main():
    rclpy.init()
    node=Talker()
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
