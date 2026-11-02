import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, 
    GroupAction, 
    RegisterEventHandler,
    TimerAction,
    OpaqueFunction,
    EmitEvent
)
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessStart
from launch_ros.actions import Node, PushRosNamespace
from launch.events import Shutdown

def generate_nodes(context, *args, **kwargs):
    # 1. 解析参数，严格对应契约
    target_ns = LaunchConfiguration('namespace').perform(context)
    input_params_file = LaunchConfiguration('params_file').perform(context)
    use_sim_val = LaunchConfiguration('use_sim_time').perform(context).lower() == 'true'

    # 2. 处理 YAML 路径
    pkg_dir = get_package_share_directory('py01')
    default_yaml1 = os.path.join(pkg_dir, 'config', 'params_robot1.yaml')
    default_yaml2 = os.path.join(pkg_dir, 'config', 'params_robot2.yaml')

    # 如果命令行传了 params_file，就用传进来的；如果是空的，就用包里默认的
    if input_params_file:
        path1 = input_params_file
        path2 = input_params_file
    else:
        path1 = default_yaml1
        path2 = default_yaml2

    # ================= 🌟 错误处理（检查文件是否存在） =================
    if target_ns in ['all', 'robot1'] and not os.path.exists(path1):
        print(f"\n\033[91m[Launch Error] 找不到参数文件: {path1}\033[0m\n")
        return [EmitEvent(event=Shutdown(reason="YAML not found"))]

    if target_ns in ['all', 'robot2'] and not os.path.exists(path2):
        print(f"\n\033[91m[Launch Error] 找不到参数文件: {path2}\033[0m\n")
        return [EmitEvent(event=Shutdown(reason="YAML not found"))]

    # 准备传给节点的配置
    params_file_1 = LaunchConfiguration('params_file')
    params_file_2 = LaunchConfiguration('params_file')

    # 把命令行传进来的 params_file 和 use_sim_time 强行塞进参数字典里
    # 这样即使 YAML 里没写，也能根据 Launch 参数生效
    override_params_1 = [params_file_1, {'use_sim_time': use_sim_val}]
    override_params_2 = [params_file_2, {'use_sim_time': use_sim_val}]

    # --- robot1 组 ---
    r1_node_A = Node(package='py01', executable='Node_A', output='screen', parameters=[{'use_sim_time': use_sim_val}])
    r1_node_B = Node(package='py01', executable='Node_B', name='node_b_filter', output='screen', parameters=override_params_1)
    r1_node_C_client = Node(package='py01', executable='Node_C_client', name='node_c_alarm', namespace='robot1', output='screen', parameters=override_params_1)
    r1_node_C_server = Node(package='py01', executable='Node_C_server', namespace='robot1', output='screen', parameters=[{'use_sim_time': use_sim_val}])

    robot1_group = GroupAction(
        actions=[
            PushRosNamespace('robot1'),
            r1_node_A,
            r1_node_B,
            RegisterEventHandler(
                event_handler=OnProcessStart(
                    target_action=r1_node_B,
                    on_start=[TimerAction(period=1.5, actions=[r1_node_C_client, r1_node_C_server])]
                )
            )
        ],
        condition=IfCondition(PythonExpression(["'", target_ns, "' == 'all' or '", target_ns, "' == 'robot1'"]))
    )

    # --- robot2 组 ---
    r2_node_A = Node(package='py01', executable='Node_A', output='screen', parameters=[{'use_sim_time': use_sim_val}])
    r2_node_B = Node(package='py01', executable='Node_B', name='node_b_filter', output='screen', parameters=override_params_2)
    r2_node_C_client = Node(package='py01', executable='Node_C_client', name='node_c_alarm', namespace='robot2', output='screen', parameters=override_params_2)
    r2_node_C_server = Node(package='py01', executable='Node_C_server', namespace='robot2', output='screen', parameters=[{'use_sim_time': use_sim_val}])

    robot2_group = GroupAction(
        actions=[
            PushRosNamespace('robot2'),
            r2_node_A,
            r2_node_B,
            RegisterEventHandler(
                event_handler=OnProcessStart(
                    target_action=r2_node_B,
                    on_start=[TimerAction(period=1.5, actions=[r2_node_C_client, r2_node_C_server])]
                )
            )
        ],
        condition=IfCondition(PythonExpression(["'", target_ns, "' == 'all' or '", target_ns, "' == 'robot2'"]))
    )

    return [robot1_group, robot2_group]

def generate_launch_description():
    return LaunchDescription([
        # 🌟 严格对齐契约表格的默认值
        DeclareLaunchArgument(
            'namespace',
            default_value='robot1',  # 契约要求默认是 robot1
            description='所有节点的命名空间'
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value='',        # 契约要求默认是空
            description='YAML 参数文件路径'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',   # 契约要求默认是 false
            description='是否使用仿真时间'
        ),
        OpaqueFunction(function=generate_nodes)
    ])