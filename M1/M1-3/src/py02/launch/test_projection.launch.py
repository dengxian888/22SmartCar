import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = get_package_share_directory('py02')
    config_file = os.path.join(pkg_dir, 'config', 'extrinsics.yaml')

    # 1. 启动静态 TF 广播节点
    # 注意：因为我们在回放 bag，所以必须设 use_sim_time 为 true
    static_tf_node = Node(
        package='py02',
        executable='static_tf_broadcaster',
        name='static_tf_broadcaster',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # 2. 播放 sample_bag 数据包
    # 这里的路径假设你是在 M1-3 根目录下执行 ros2 launch
    bag_path = os.path.join(os.getcwd(), 'sample_bag')
    play_bag = ExecuteProcess(
        cmd=['ros2', 'bag', 'play', bag_path, '--clock', '-l'], # -l 表示循环播放
        output='screen'
    )

    # 3. 启动同步与投影节点（延迟 1 秒启动，等 TF 和 bag 准备好）
    sync_node = Node(
        package='py02',
        executable='sync_node',
        name='sync_node',
        parameters=[
            {'use_sim_time': True},
            {'slop': 0.019}
        ],
        output='screen'
    )
    delay_sync_node = TimerAction(
        period=1.0, # 延迟 1 秒
        actions=[sync_node]
    )

    # 4. （可选）自动打开 RViz
    # 如果你想让 launch 顺便把 RViz 也打开了，可以取消注释下面这段
    # rviz_node = Node(
    #     package='rviz2',
    #     executable='rviz2',
    #     name='rviz2',
    #     parameters=[{'use_sim_time': True}],
    #     output='screen'
    # )

    return LaunchDescription([
        static_tf_node,
        play_bag,
        delay_sync_node,
        # rviz_node
    ])