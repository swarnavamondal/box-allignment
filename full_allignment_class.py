from ultralytics import YOLO
import cv2
import numpy as np

class BoxAligner:
    def __init__(self, model_path, video_source=0, save_path=None):
        """
        Initialize the box alignment system.

        Args:
            model_path (str): Path to the trained YOLO model.
            video_source (int or str): Camera index or video path.
            save_path (str, optional): File path to save the annotated image. If None, display window instead.
        """
        self.model = YOLO(model_path)
        self.cap = cv2.VideoCapture(video_source)
        self.save_path = save_path

        if not self.cap.isOpened():
            print("Could not open video source.")
            exit()

        # Define parameters
        self.lower_blue = np.array([90, 70, 50])
        self.upper_blue = np.array([130, 255, 255])
        self.min_area = 70000
        self.max_area = 80000
        self.margin = 150

    def run(self):
        """Run the alignment detection loop."""
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Resize for consistency
            frame = cv2.resize(frame, (640, 480))
            height, width, _ = frame.shape
            centre = width // 2

            # YOLO detection
            results = self.model.predict(source=frame, conf=0.5, verbose=False)

            # Convert to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)

            # Draw reference lines
            cv2.line(frame, (centre - self.margin, 0), (centre - self.margin, height), (255, 255, 255), 2)
            cv2.line(frame, (centre + self.margin, 0), (centre + self.margin, height), (255, 255, 255), 2)

            annotated_frame = frame.copy()

            # Process YOLO boxes
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = results[0].names[cls]

                roi = mask[y1:y2, x1:x2]
                blue_ratio = (cv2.countNonZero(roi) / roi.size) if roi.size > 0 else 0

                if blue_ratio > 0.3:
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(annotated_frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

                    cv2.line(annotated_frame, (x1, y1), (x1, y2), (255, 255, 0), 4)
                    cv2.line(annotated_frame, (x2, y1), (x2, y2), (255, 255, 0), 4)

                    area = (x2 - x1) * (y2 - y1)
                    cv2.putText(annotated_frame, f"area: {area}", (70, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    #print(area)
                    areaDifference = 0
                    # Area control
                    if area < self.min_area:
                        areaDifference = self.min_area - area
                        cv2.putText(annotated_frame, "move forward", (70, 300),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    elif area > self.max_area:
                        areaDifference=self.max_area-area
                        cv2.putText(annotated_frame, "move backward", (70, 300),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    print("areadiff",areaDifference)

                    # Alignment control
                    xdifference = 0
                    if x1 < (centre - self.margin):
                        xdifference=x1-(centre-self.margin)
                        cv2.putText(annotated_frame, "move left", (70, 200),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    elif x2 > (centre + self.margin):
                        xdifference=x2-(centre+self.margin)
                        cv2.putText(annotated_frame, "move right", (70, 200),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    print("xdifference",xdifference)

                    # Status indicators
                    if self.min_area <= area <= self.max_area:
                        cv2.putText(annotated_frame, "Z-Box aligning", (200, 400),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    else:
                        cv2.putText(annotated_frame, "Z-Box not aligning", (200, 400),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                    if x1 >= (centre - self.margin) and x2 <= (centre + self.margin):
                        cv2.putText(annotated_frame, "X-Box aligning", (200, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    else:
                        cv2.putText(annotated_frame, "Box not aligning", (200, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.imwrite(r"/home/ghost/Desktop/swarnava/box-allignment/img.png", annotated_frame)


# Example usage:
if __name__ == "__main__":
    aligner = BoxAligner(
        model_path=r"/home/ghost/Desktop/swarnava/box-allignment/best (1).pt",
        video_source=0,
        save_path=r"/home/ghost/Desktop/swarnava/box-allignment/img.png"
    )
    aligner.run()
