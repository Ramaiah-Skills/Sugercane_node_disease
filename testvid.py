import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
from picamera2 import Picamera2  # Import Raspberry Pi camera library

MARGIN = -1  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
rect_color = (255, 0, 255)  # magenta
TEXT_COLOR = (255, 0, 0)  # red

# Initialize Picamera2
picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={"size": (640, 480)})
picam2.configure(camera_config)
picam2.start()

base_options = python.BaseOptions(model_asset_path='best.tflite')
options = vision.ObjectDetectorOptions(base_options=base_options,
                                       score_threshold=0.5)
detector = vision.ObjectDetector.create_from_options(options)

while True:
    # Capture frame from Raspberry Pi Camera
    frame = picam2.capture_array()

    # Flip the frame if needed (horizontal flip)
    frame = cv2.flip(frame, 1)
    
    # Convert the frame to an Image format suitable for MediaPipe
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

    # Run object detection
    detection_result = detector.detect(mp_image)
    
    for detection in detection_result.detections:
        # Get bounding box coordinates
        bbox = detection.bounding_box
        x = int(bbox.origin_x)
        y = int(bbox.origin_y)
        w = int(bbox.width)
        h = int(bbox.height)
    
        # Draw rectangle around the object
        start_point = (x, y)
        end_point = (x + w, y + h)
        cv2.rectangle(frame, start_point, end_point, rect_color, 3)

        # Get category and probability
        category = detection.categories[0]
        category_name = category.category_name
        probability = round(category.score, 2)
        result_text = f"{category_name} ({probability})"

        # Set text location above the rectangle
        text_location = (x, y - 10)  # Adjust if necessary

        # Put text on the image
        cv2.putText(frame, result_text, text_location, cv2.FONT_HERSHEY_PLAIN, FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

    # Display the frame with bounding boxes and labels
    cv2.imshow("test window", frame)

    # Break the loop if ESC key is pressed
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Release resources and close windows
picam2.stop()
cv2.destroyAllWindows()
