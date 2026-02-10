from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Start the micro-ROS Agent
        Node(
            package='micro_ros_agent',
            executable='micro_ros_agent',
            name='micro_ros_agent',
            arguments=['serial', '--dev', '/dev/ttyACM0'],
            output='screen'
        ),

        # 2. Start your Python Publisher Node
        Node(
            package='your_package_name', # Replace with your actual package name
            executable='talker_node.py', # Ensure this is marked as executable
            name='python_publisher',
            output='screen'
        )
    ])