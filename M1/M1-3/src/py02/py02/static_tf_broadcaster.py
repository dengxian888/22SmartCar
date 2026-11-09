import rclpy
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster #静态坐标发布器
from geometry_msgs.msg import TransformStamped #消息接口
from tf_transformations import quaternion_from_euler #欧拉角转四元数函数
import math #角度转弧度函数
import yaml
import os
from geometry_msgs.msg import TransformStamped
from ament_index_python.packages import get_package_share_directory
from builtin_interfaces.msg import Time

    

class StaticTFBroadcaster(Node):
    def __init__(self):
        super().__init__('static_tf_broadcaster')
        self.broadcaster = StaticTransformBroadcaster(self)
        pkg_path = get_package_share_directory('py02')
        yaml_path = os.path.join(pkg_path, 'config', 'extrinsics.yaml')


        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
            
        laser_link = config['laser_link']
        parent_frame=config['laser_link']['parent']
        xyz = config['laser_link']['xyz']
        rpy = config['laser_link']['rpy']
        t_laser=self.create_static_tf('laser_link', parent_frame, xyz, rpy)
        
        camera_link = config['camera_link']
        parent_frame=config['camera_link']['parent']
        xyz = config['camera_link']['xyz']
        rpy = config['camera_link']['rpy']
        t_camera=self.create_static_tf('camera_link', parent_frame, xyz, rpy)
        
        self.broadcaster.sendTransform([t_laser, t_camera])
        self.get_logger().info('成功发布静态TF.')

    def create_static_tf(self,child_frame_id, parent_frame_id, xyz, rpy):
        t = TransformStamped()
        t.header.stamp = Time()
        t.header.frame_id = parent_frame_id #父坐标系
        t.child_frame_id = child_frame_id #子坐标系

        #设置平移
        t.transform.translation.x = xyz[0]
        t.transform.translation.y = xyz[1]
        t.transform.translation.z = xyz[2]

        #设置旋转（欧拉角转四元数）
        q = quaternion_from_euler(rpy[0], rpy[1], rpy[2])
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]

        return t

def main(args=None):
    rclpy.init(args=args)
    node = StaticTFBroadcaster()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass # 按下 Ctrl+C 时静默退出
    node.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()