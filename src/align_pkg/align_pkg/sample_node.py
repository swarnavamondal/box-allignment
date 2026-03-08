#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

class SampleNode(Node):
    def __init__(self):
        super().__init__("first_node")
        self.c = 0
        self.get_logger().info("hello world")
        self.create_timer(0.5, self.timer_callback)

    def timer_callback(self):
        self.get_logger().info("hello " + str(self.c))
        self.c += 1
def main(args=None):
    rclpy.init(args=args)

    node = SampleNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()