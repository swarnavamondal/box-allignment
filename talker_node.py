import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32  # Using Int32 for simplicity

class PythonPublisher(Node):
    def __init__(self):
        super().__init__('python_publisher_node')
        # We publish to the "teensy_topic"
        self.publisher_ = self.create_publisher(Int32, 'teensy_topic', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.count = 0

    def timer_callback(self):
        msg = Int32()
        msg.data = self.count
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')
        self.count += 1

def main(args=None):
    rclpy.init(args=args)
    node = PythonPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()