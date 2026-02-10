from ultralytics import YOLO
import cv2
import numpy as np

# --- Load your trained YOLOv8 model ---
model = YOLO(r'/home/swarnava/Arduino/robocon 2026/box-allignment_7feb/box-allignment/best (1).pt')  # path to your trained weights

# --- Path to your input video ---
#video_path = 'WIN_20251107_22_55_26_Pro.mp4'
cap = cv2.VideoCapture(4)
if not cap.isOpened():
    print("Could not open video file.")
    exit()

# --- Define blue color range in HSV ---
lower_blue = np.array([90, 70, 50])    
upper_blue = np.array([130, 255, 255])

min_area = 70000
max_area = 80000
margin = 150

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Optional: resize for faster processing
    frame = cv2.resize(frame, (640, 480))

    height, width, _ = frame.shape
    centre = width // 2
    

    # --- YOLO detection ---
    results = model.predict(source=frame, conf=0.5, verbose=False)

    # --- Convert to HSV for color filtering ---
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # --- Create mask for blue color ---
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    cv2.line(frame, (centre-margin,0),(centre-margin, height), (255,255,255), 2)
    cv2.line(frame, (centre+margin,0),(centre+margin, height), (255,255,255), 2)

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
        if blue_ratio > 0.3:  # 30% of region is blue
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(annotated_frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            cv2.line(annotated_frame,(x1,y1),(x1,y2),(255,255,0),4)
            cv2.line(annotated_frame,(x2,y1),(x2,y2),(255,255,0),4)

            area = (x2 - x1) * (y2 - y1)
            cv2.putText(annotated_frame, f"area: {area}", (70, 30),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            

            # Determine area difference from target range
            areadifference=0
            if area<min_area:
                areadifference=min_area-area
                cv2.putText(annotated_frame,"move forward", (70, 300),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            elif area>max_area:
                areadifference=max_area-area
                cv2.putText(annotated_frame,"move backward", (70, 300),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            # Display alignment status
            xdifference=0
            if x1 < (centre - margin):
                xdifference=(centre - margin) - x1
                cv2.putText(annotated_frame,"move left", (70, 200),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            elif x2 > (centre + margin):
                xdifference=(centre + margin) - x2
                cv2.putText(annotated_frame,"move right", (70, 200),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            if area >=min_area and area <= max_area:
                cv2.putText(annotated_frame, "Z-Box aligning", (200, 400),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(annotated_frame, "Z-Box not aligning", (200, 400),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if x1 >= (centre - margin) and x2 <= (centre + margin):
                cv2.putText(annotated_frame, "X-Box aligning", (200, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(annotated_frame, "Box not aligning", (200, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            print(areadifference,xdifference)




    # --- Display the result ---
    # cv2.imshow("YOLO + HSV Blue Detection", annotated_frame)
    cv2.imwrite(r'/home/swarnava/Arduino/robocon 2026/box-allignment_7feb/box-allignment/img.png', annotated_frame)

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

cap.release()
cv2.destroyAllWindows()
