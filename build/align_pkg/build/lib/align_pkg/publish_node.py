#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class Messages(Node):

    def __init__(self):
        super().__init__("messages_node")

        # Create publisher for Float32 messages
        self.publisher_ = self.create_publisher(
            Float32,
            "float_topic",
            10  # QoS depth
        )

        # Publish at 2 Hz
        self.timer = self.create_timer(0.5, self.publish_float)

        self.value = 0.0
        self.get_logger().info("Publishing float values...")

    def publish_float(self):
        msg = Float32()
        msg.data = self.value

        self.publisher_.publish(msg)
        self.get_logger().info(f"Published: {msg.data}")

        self.value += 1.0


def main(args=None):
    rclpy.init(args=args)

    node = Messages()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()