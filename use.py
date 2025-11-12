from ultralytics import YOLO
import cv2

# --- Load your trained YOLOv8 model ---
model = YOLO('best (1).pt')  # path to your downloaded weights

# --- Path to your video ---
video_path = 'WhatsApp Video 2025-11-08 at 19.31.07.mp4'  # change to your video filename
cap = cv2.VideoCapture(2)

# --- Check if video opened successfully ---
if not cap.isOpened():
    print("❌ Error: Could not open video file.")
    exit()

# --- Read video frames and perform detection ---
while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))  # Resize frame for consistency
    if not ret:
        break

    # Run YOLOv8 inference
    results = model.predict(source=frame, conf=0.5, verbose=False)

    # Draw bounding boxes and labels
    annotated_frame = results[0].plot()

    # Display the frame
    cv2.imshow('YOLOv8 Detection', annotated_frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Clean up ---
cap.release()
cv2.destroyAllWindows()
