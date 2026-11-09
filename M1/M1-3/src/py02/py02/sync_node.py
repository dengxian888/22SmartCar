import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image,CameraInfo
from message_filters import Subscriber, ApproximateTimeSynchronizer
import statistics # Python 自带的统计库
from math import isnan
import math
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import tf_transformations
import yaml
import os
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
import cv2
import numpy as np
from std_msgs.msg import Header

class SyncNode(Node):
    def __init__(self):
        super().__init__('sync_node')
        
        # 1. 声明参数（带默认值）
        self.declare_parameter('slop', 0.05)      # 默认 50ms
        self.declare_parameter('queue_size', 60)  # 默认队列长度 50
        self.declare_parameter('output_dir', '.')      # 默认保存到当前目录
        self.declare_parameter('max_images', 3)        # 默认最多保存3张
        self.get_logger().info(f'当前节点的 use_sim_time 设置为: {self.get_parameter("use_sim_time").value}')
        
        
        self.dt_list = [] # 用来存每次配对的时间差
        
        # 2. 获取参数
        slop = self.get_parameter('slop').value
        queue_size = self.get_parameter('queue_size').value
        self.get_logger().info(f'启动同步节点，slop={slop}, queue={queue_size}')

        # 3. 创建 message_filters 专用的 Subscriber
        # 注意：这里不是 self.create_subscription，而是 message_filters.Subscriber
        self.scan_sub = Subscriber(self, LaserScan, '/scan')
        self.image_sub = Subscriber(self, Image, '/camera/image_raw')
        
        # 4. 创建 TF2 监听器
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # 5. 创建近似时间同步器
        self.ts = ApproximateTimeSynchronizer(
            [self.scan_sub, self.image_sub],
            queue_size=queue_size,
            slop=slop
        )
        # 6. 注册回调函数
        self.ts.registerCallback(self.sync_callback)

        self.match_count = 0 # 记录配对次数
        
       # 初始化内参默认值（防止首帧数据到达时还未收到 camera_info）
        self.fx = 0.0
        self.fy = 0.0
        self.cx = 0.0
        self.cy = 0.0
        self.has_intrinsics = False

        # 订阅相机信息话题
        self.create_subscription(CameraInfo, '/camera/camera_info', self.info_callback, 10)
        self.get_logger().info('等待接收相机内参...')
        
        #创建投影发布者
        self.bridge = CvBridge()
        self.pub = self.create_publisher(Image, '/projection/debug_image', 10)
        


        self.output_dir = self.get_parameter('output_dir').value
        self.max_images = self.get_parameter('max_images').value
        self.saved_count = 0
                
    def info_callback(self, msg):
        # CameraInfo 里的 k 数组就是内参矩阵 [fx, 0, cx, 0, fy, cy, 0, 0, 1]
        self.fx = msg.k[0]
        self.cx = msg.k[2]
        self.fy = msg.k[4]
        self.cy = msg.k[5]
        
        if not self.has_intrinsics:
            self.get_logger().info(f'✅ 成功接收相机内参: fx={self.fx}, fy={self.fy}, cx={self.cx}, cy={self.cy}')
            self.has_intrinsics = True

    def sync_callback(self, scan_msg, image_msg):
        if not self.has_intrinsics:
            self.get_logger().warn('尚未接收到相机内参，跳过当前帧处理.')
            return
        self.get_logger().info(f"Node time: {self.get_clock().now().to_msg().sec}")
        try:
            self.match_count += 1
            
            # 计算时间差（单位：毫秒）
            scan_t = scan_msg.header.stamp.sec + scan_msg.header.stamp.nanosec * 1e-9
            img_t = image_msg.header.stamp.sec + image_msg.header.stamp.nanosec * 1e-9
            dt_ms = abs(scan_t - img_t) * 1000.0
            self.dt_list.append(dt_ms)
            
            # 1. 找搬运工
            t = self.tf_buffer.lookup_transform('camera_link', 'laser_link', scan_msg.header.stamp)
            
            # 2. 组建运输车 (4x4矩阵)
            trans = [t.transform.translation.x, t.transform.translation.y, t.transform.translation.z]
            rot = [t.transform.rotation.x, t.transform.rotation.y, t.transform.rotation.z, t.transform.rotation.w]
            T = tf_transformations.quaternion_matrix(rot)
            T[0:3, 3] = trans

            # 统计一下这一帧里有多少点能看到
            valid_points = 0

            # 把 ROS 图像转成 OpenCV 格式（BGR）
            cv_image = self.bridge.imgmsg_to_cv2(image_msg, desired_encoding='bgr8')
            
            # 3. 遍历雷达点云
            for i, r in enumerate(scan_msg.ranges):#enumerate 是 Python 的一个工具，它会返回两个东西：i（这是第几个数据）和 r（具体的距离值）
                # 过滤无效点（太近、太远或 nan）
                if r < scan_msg.range_min or r > scan_msg.range_max or math.isnan(r):
                    continue
                    
                angle = scan_msg.angle_min + i * scan_msg.angle_increment #angle_increment是每个点之间的角度增量，angle_min是第一个点的角度
                # 雷达坐标系下的 3D 点，极坐标转直角坐标
                x_laser = r * math.cos(angle)
                y_laser = r * math.sin(angle)
                z_laser = 0.0
            
                # 开始搬运到相机坐标系
                p_laser = [x_laser, y_laser, z_laser, 1.0]
                p_camera = T.dot(p_laser)
                X_c, Y_c, Z_c = p_camera[0], p_camera[1], p_camera[2]

                # 坐标系转换 (假设你的 camera_link 是 X前 Y左 Z上)
                # 根据任务说明，这里用光学坐标系计算
                X_opt = -Y_c
                Y_opt = -Z_c
                Z_opt = X_c


                # 必须在相机前面
                if Z_opt > 0:
                    u = int((self.fx * X_opt) / Z_opt + self.cx)
                    v = int((self.fy * Y_opt) / Z_opt + self.cy) 

                    # 判断是否在图像范围内
                    if 0 <= u < image_msg.width and 0 <= v < image_msg.height:
                        # ★★★ 开始画图 ★★★
                        # 根据距离 r 计算颜色 (近处 r 小为红，远处 r 大为蓝)
                        # 假设有效距离是 0.5米到 8.0米
                        ratio = min(max((r - 0.5) / (8.0 - 0.5), 0.0), 1.0)
                        # BGR 格式: (蓝, 绿, 红)
                        color = (int(255 * ratio), 0, int(255 * (1 - ratio)))
                        
                        # 在图像上画实心圆
                        cv2.circle(cv_image, (u, v), 10, color, -1)
                        valid_points += 1
        
            # ★★★ 发布画好图的图像 ★★★
            # 记得更新 header，这样 rviz 里时间对齐才不会报错
            debug_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8')
            debug_msg.header = image_msg.header 
            self.pub.publish(debug_msg)

            self.get_logger().info(f'共找到 {valid_points} 个点，已发布到 /projection/debug_image')
            
            # 保存效果图
            if self.saved_count < self.max_images:
                # 构造文件名，例如 projection_1.png, projection_2.png
                filename = os.path.join(
                    self.output_dir,
                    f'projection_{self.saved_count + 1}.png'
                )
                # 使用 OpenCV 保存图像（cv_image 是你画好点的 BGR 图像）
                success = cv2.imwrite(filename, cv_image)
                if success:
                    self.saved_count += 1
                    self.get_logger().info(
                        f'📸 已保存第 {self.saved_count} 张效果图: {filename}'
                    )

        except Exception as e:
            self.get_logger().warn(f'TF查询或处理失败: {e}')
            

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