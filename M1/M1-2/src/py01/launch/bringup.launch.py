import launch
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument,GroupAction
from launch.substitutions import LaunchConfiguration,PythonExpression
from launch_ros.actions import Node,PushRosNamespace
from launch.conditions import IfCondition



def generate_launch_description():
    
    #声明 Launch 参数 params_file，默认指向包的 config 目录
    params_file_1_arg = DeclareLaunchArgument(
        'params_file_1',
        default_value=os.path.join(
            get_package_share_directory('py01'), 'config', 'params_robot1.yaml'
        ),
        description='Path to robot1 params file'
    )
    
    params_file_2_arg = DeclareLaunchArgument(
        'params_file_2',
        default_value=os.path.join(
            get_package_share_directory('py01'), 'config', 'params_robot2.yaml'
        ),
        description='Path to robot2 params file'
    )
    
    
    declare_namespace = DeclareLaunchArgument(
        'namespace',
        default_value='all',
        description='Choose which robot to run: robot1, robot2, or all'
    )
    
    
    params_file_1 = LaunchConfiguration('params_file_1')
    params_file_2 = LaunchConfiguration('params_file_2')
    target_ns=LaunchConfiguration('namespace')
    
    run_robot1 = LaunchConfiguration('run_robot1')
    run_robot2 = LaunchConfiguration('run_robot2')
    
    #配置robot1组
    robot1_group=GroupAction(
        actions=[
        PushRosNamespace('robot1'),
        
        Node(
            package='py01',
            executable='Node_A',
            output='screen'
            ),
            
        
        Node(
            package='py01',
            executable='Node_B',
            name='node_b_filter',
            output='screen',
            parameters=[params_file_1]
            ),
        Node(
            package='py01',
            executable='Node_C_client',
            name='node_c_alarm',
            output='screen',
            parameters=[params_file_1]
        ),
        Node(
            package='py01',
            executable='Node_C_server',
            output='screen'
        )
    ],
        condition=IfCondition(PythonExpression(["'",target_ns,"'=='all'or'",target_ns,"'=='robot1'"]))
        )
    
    #配置robot2组
    robot2_group=GroupAction(
        actions=[
        PushRosNamespace('robot2'),
        
        Node(
            package='py01',
            executable='Node_A',
            output='screen'
            ),
            
        Node(
            package='py01',
            executable='Node_B',
            name='node_b_filter',
            output='screen',
            parameters=[params_file_2]
            ),
        Node(
            package='py01',
            executable='Node_C_client',
            name='node_c_alarm',
            output='screen',
            parameters=[params_file_2]
        ),
        Node(
            package='py01',
            executable='Node_C_server',
            output='screen'
        )
    ],
    condition=IfCondition(PythonExpression(["'", target_ns, "' == 'all' or '", target_ns, "' == 'robot2'"]))
        )
    

        
    
    return launch.LaunchDescription([
            params_file_1_arg,
            params_file_2_arg,
            declare_namespace,
            robot1_group,
            robot2_group
        ])