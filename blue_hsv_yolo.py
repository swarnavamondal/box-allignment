from ultralytics import YOLO
import cv2
import numpy as np

# --- Load your trained YOLOv8 model ---
model = YOLO('best (1).pt')  # path to your trained weights

# --- Path to your input video ---
video_path = 'WIN_20251107_22_55_26_Pro.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("❌ Could not open video file.")
    exit()

# --- Define blue color range in HSV ---
lower_blue = np.array([90, 70, 50])    # adjust if needed
upper_blue = np.array([130, 255, 255])

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Optional: resize for faster processing
    frame = cv2.resize(frame, (640, 480))

    # --- YOLO detection ---
    results = model.predict(source=frame, conf=0.5, verbose=False)

    # --- Convert to HSV for color filtering ---
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # --- Create mask for blue color ---
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # --- Annotate YOLO detections ---
    annotated_frame = frame.copy()

    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])  # bounding box
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        label = results[0].names[cls]

        # Extract ROI and check for blue color inside
        roi = mask[y1:y2, x1:x2]
        blue_ratio = (cv2.countNonZero(roi) / roi.size) if roi.size > 0 else 0

        # Only show boxes if mostly blue
        if blue_ratio > 0.2:  # 20% of region is blue
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(annotated_frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # --- Display the result ---
    cv2.imshow("YOLO + HSV Blue Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
