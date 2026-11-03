import rclpy
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster #静态坐标发布器
from geometry_msgs.msg import TransformStamped #消息接口
from tf_transformations import quaternion_from_euler #欧拉角转四元数函数
import math #角度转弧度函数

class StaticTFBroadcaster(Node):
    def __init__(self):
        super().__init__('static_tf_broadcaster')
        self.broadcaster = StaticTransformBroadcaster(self)
        self.timer = self.create_timer(1.0, self.publish_static_tf) #每秒发布一次静态坐标变换

    def publish_static_tf(self):
        static_transform_stamped = TransformStamped()

        static_transform_stamped.header.stamp = self.get_clock().now().to_msg()
        static_transform_stamped.header.frame_id = 'world' #父坐标系
        static_transform_stamped.child_frame_id = 'base_link' #子坐标系

        #设置平移
        static_transform_stamped.transform.translation.x = 1.0
        static_transform_stamped.transform.translation.y = 2.0
        static_transform_stamped.transform.translation.z = 3.0

        #设置旋转（欧拉角转四元数）
        roll = math.radians(30) #绕x轴旋转30度
        pitch = math.radians(45) #绕y轴旋转45度
        yaw = math.radians(60) #绕z轴旋转60度
        q = quaternion_from_euler(roll, pitch, yaw)
        static_transform_stamped.transform.rotation.x = q[0]
        static_transform_stamped.transform.rotation.y = q[1]
        static_transform_stamped.transform.rotation.z = q[2]
        static_transform_stamped.transform.rotation.w = q[3]

        self.broadcaster.sendTransform(static_transform_stamped)