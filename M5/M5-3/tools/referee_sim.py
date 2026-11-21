import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import sys, termios, tty, threading
import argparse

class RefereeSimulator(Node):
    def __init__(self):
        super().__init__('referee_simulator')
        self.pub = self.create_publisher(String, '/referee/cmd', 10)
        self.get_logger().info("裁判模拟器已启动。按 S=START, P=PAUSE, R=RESUME, E=STOP, Q=退出")

    def send_cmd(self, cmd):
        msg = String()
        msg.data = cmd
        self.pub.publish(msg)
        self.get_logger().info(f"发送裁判指令: {cmd}")

def keyboard_listener(node):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while rclpy.ok():
            ch = sys.stdin.read(1).upper()
            if ch == 'S': node.send_cmd("START")
            elif ch == 'P': node.send_cmd("PAUSE")
            elif ch == 'R': node.send_cmd("RESUME")
            elif ch == 'E': node.send_cmd("STOP")
            elif ch == 'Q': 
                node.get_logger().info("退出模拟器")
                rclpy.shutdown()
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def main():
    # 新增：显式支持 --mode 参数
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default='keyboard', choices=['keyboard'], 
                        help="运行模式：keyboard (键盘模拟)")
    args = parser.parse_args()

    rclpy.init()
    node = RefereeSimulator()
    
    if args.mode == 'keyboard':
        # 开启键盘监听线程
        threading.Thread(target=keyboard_listener, args=(node,), daemon=True).start()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            if rclpy.ok():
                node.destroy_node()
                rclpy.shutdown()

if __name__ == '__main__':
    main()