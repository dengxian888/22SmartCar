import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from rclpy.parameter import Parameter

class MockPerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')
        # 声明参数 model_path，默认值为 /models/default.engine
        self.declare_parameter('model_path', '/models/default.engine')
        
        # 注册参数变更回调
        self.add_on_set_parameters_callback(self.param_callback)
        
        current_model = self.get_parameter('model_path').value
        self.get_logger().info(f"✅ 感知节点启动完毕，当前加载模型: {current_model}")
        self.get_logger().info("PID: 记一下哦，等下热切的时候我不会重启的。")

    def param_callback(self, params):
        for param in params:
            if param.name == 'model_path':
                new_path = param.value
                self.get_logger().info(f"🔄 收到动态参数更新请求: 准备热加载模型 -> {new_path}")
                
                # 模拟模型加载耗时
                import time
                time.sleep(0.5) 
                
                # 假设这里做了一些文件检查，如果文件名包含 "bad" 就拒绝加载模拟失败
                if "bad" in new_path:
                    self.get_logger().error("❌ 模型加载失败：找不到文件或格式不支持")
                    return SetParametersResult(successful=False, reason="bad model")
                
                self.get_logger().info(f"✅ 模型热加载成功！已切换至: {new_path} (底层进程未重启)")
                return SetParametersResult(successful=True)
                
        return SetParametersResult(successful=True)

def main():
    rclpy.init()
    node = MockPerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()