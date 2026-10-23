import rclpy
from rclpy.node import Node
from sensor_interfaces.msg import SensorData
from std_msgs.msg import Float32
from rcl_interfaces.msg import SetParametersResult

class Listener(Node):
    def __init__(self):
        super().__init__("listener_node_py")
        self.get_logger().info("订阅方创建")
        self.subscription=self.create_subscription(SensorData,"sensor_data",self.listener_callback,10)
        self.publisher= self.create_publisher(Float32, '/processed_distance', 10)

        #声明动态参数 alpha，默认值 0.3
        self.declare_parameter('alpha', 0.3)
        self.alpha = self.get_parameter('alpha').value
        
        #注册参数改变回调，使得 ros2 param set 能立刻生效
        self.add_on_set_parameters_callback(self.parameter_callback)
        
        #用于保存上一次的滤波结果 (y_{k-1})
        self.y_prev = None 

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'alpha':
                # 当在终端修改参数时，更新内部的 self.alpha 变量
                self.alpha = param.value 
                self.get_logger().info(f"动态参数更新: alpha 变更为 {self.alpha}")
        return SetParametersResult(successful=True)

    
    def listener_callback(self, msg):
        #滤除无效数据,打印警告
        if msg.status != 0:
            self.get_logger().warn(f"无效数据！状态:{msg.status}，已跳过滤波。")
            return
        
        if self.y_prev is None:
            #第一帧有效数据，直接赋值
            y_k = msg.distance
        else:
            # 套用公式：y_k = alpha * x_k + (1 - alpha) * y_{k-1}
            y_k = self.alpha * msg.distance + (1.0 - self.alpha) * self.y_prev
            
        # 更新历史值，为下一帧做准备
        self.y_prev = y_k
        
        # 发布结果
        out_msg = Float32()
        out_msg.data = float(y_k)
        self.publisher.publish(out_msg)
        
        self.get_logger().info(f"原始: {msg.distance:.2f} -> 滤波后: {y_k:.2f}")
    
def main():
    rclpy.init()
    node=Listener()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__=='__main__':
    main()