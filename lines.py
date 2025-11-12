import cv2

# Open the default camera (0)
cap = cv2.VideoCapture(0)


if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Press 'q' to quit the window.")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture frame.")
        break
    #frame=cv2.flip(frame,1)

    frame = cv2.resize(frame, (640, 480))
    frame = cv2.flip(frame, 1)
    #drawing lines
    height, width, _ = frame.shape
    centre = width // 2
    margin = 100

    cv2.line(frame, (centre-margin,0),(centre-margin, height), (255,255,255), 2)
    cv2.line(frame, (centre+margin,0),(centre+margin, height), (255,255,255), 2)

    # Display the resulting frame
    cv2.imshow("Webcam Test", frame)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
