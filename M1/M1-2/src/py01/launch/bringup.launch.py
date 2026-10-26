import launch
import launch_ros

def generate_launch_description():
    action_node_A=launch_ros.actions.Node(
        package='py01',
        executable='Node_A',
        output='screen'
        
    )
    
    action_node_B=launch_ros.actions.Node(
        package='py01',
        executable='Node_B',
        output='screen'
        
    )
    
    action_node_C_client=launch_ros.actions.Node(
        package='py01',
        executable='Node_C_client',
        output='screen'
    )
        
    action_node_C_server=launch_ros.actions.Node(
        package='py01',
        executable='Node_C_server',
        output='screen'
        
    )
        
    
    return launch.LaunchDescription([
            #actions
            action_node_A,
            action_node_B,
            action_node_C_client,
            action_node_C_server
        ])