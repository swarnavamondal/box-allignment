#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3

from ultralytics import YOLO
import cv2
import numpy as np


class BoxAlignerNode(Node):

    def __init__(self):
        super().__init__("box_aligner_node")

        # Publisher
        self.publisher_ = self.create_publisher(
            Vector3,
            "alignment_error",
            10
        )

        # Load YOLO model
        self.model = YOLO(
            "/home/swarnava/Arduino/robocon 2026/symbol_detect/final2.pt"
        )

        # Camera
        self.cap = cv2.VideoCapture(4)
        if not self.cap.isOpened():
            self.get_logger().error("Could not open camera.")
            rclpy.shutdown()

        # Parameters
        self.lower_blue = np.array([90, 70, 50])
        self.upper_blue = np.array([130, 255, 255])
        self.min_area = 70000
        self.max_area = 80000
        self.margin = 150

        # Timer
        self.timer = self.create_timer(1.00/30.0, self.process_frame)  # ~20 Hz

        self.get_logger().info("Box Aligner Node Started")

    def process_frame(self):

        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.resize(frame, (640, 480))
        height, width, _ = frame.shape
        centre = width // 2

        annotated_frame = frame.copy()

        # Draw margin lines
        cv2.line(annotated_frame, (centre - self.margin, 0),
                 (centre - self.margin, height), (255, 255, 255), 2)
        cv2.line(annotated_frame, (centre + self.margin, 0),
                 (centre + self.margin, height), (255, 255, 255), 2)

        results = self.model.predict(source=frame, conf=0.5, verbose=False)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)

        xdifference = 0.0
        areaDifference = 0.0

        for box in results[0].boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = results[0].names[cls]

            roi = mask[y1:y2, x1:x2]
            blue_ratio = (cv2.countNonZero(roi) / roi.size) if roi.size > 0 else 0

            if blue_ratio > 0.3:

                # Draw bounding box
                cv2.rectangle(annotated_frame, (x1, y1),
                              (x2, y2), (255, 0, 0), 2)

                cv2.putText(annotated_frame,
                            f"{label} {conf:.2f}",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (255, 0, 0), 2)

                area = (x2 - x1) * (y2 - y1)

                # Area control
                if area < self.min_area:
                    areaDifference = float(self.min_area - area)
                elif area > self.max_area:
                    areaDifference = float(self.max_area - area)

                # X alignment
                if x1 < (centre - self.margin):
                    xdifference = float(x1 - (centre - self.margin))
                elif x2 > (centre + self.margin):
                    xdifference = float(x2 - (centre + self.margin))

                break  # only first valid detection

        # Publish errors
        msg = Vector3()
        msg.x = xdifference
        msg.y = areaDifference
        msg.z = 0.0
        self.publisher_.publish(msg)
        self.get_logger().info(f"xDifference: {xdifference:.2f}, areaDifference: {areaDifference:.2f}")

        # Display values on frame
        cv2.putText(annotated_frame,
                    f"xDiff: {xdifference}",
                    (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0), 2)

        cv2.putText(annotated_frame,
                    f"areaDiff: {areaDifference}",
                    (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0), 2)

        # Show window
        cv2.imshow("Box Alignment", annotated_frame)

        # Press Q to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cap.release()
            cv2.destroyAllWindows()
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)

    node = BoxAlignerNode()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()