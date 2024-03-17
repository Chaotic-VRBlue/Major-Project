import cv2
import numpy as np
from ultralytics import YOLO
import tensorflow as tf
import os

# Load YOLOv5
model = YOLO(r'C:\Users\ramesh\Desktop\mainproject\Object Detection\yolov8 tomoto\best.pt')
cnn_model = tf.keras.models.load_model('cnn/tomato_255_32_cnn.h5')
names = ['ripe', 'ripe', 'ripe', 'unripe']

# Output directory for storing detected tomato images
output_directory = 'detected_tomatoes'
os.makedirs(output_directory, exist_ok=True)

# Grid parameters
num_rows = 3
num_cols = 3
grid_width_cm = 6
grid_height_cm = 6

# Function to detect objects using YOLOv
def detect_objects(frame):
    results = model(frame)
    detected_boxes, detected_cls, detected_conf = [], [], []
    for result in results:
        boxes = result.boxes.xyxy  # get box coordinates in (top, left, bottom, right) format
        conf = result.boxes.conf   # confidence scores
        cls = result.boxes.cls
        for i in range(len(boxes)):
            if conf[i] > 0.8 and conf[i] < 0.88:
                detected_boxes.append(boxes[i])
                detected_cls.append(cls[i])
                detected_conf.append(conf[i])
    return detected_boxes, detected_cls, detected_conf

# Function to calculate distance from center
def calculate_distance_from_center(x1, y1, x2, y2, frame_width, frame_height):
    # Calculate the center of the bounding box
    box_center_x = (x1 + x2) / 2
    box_center_y = (y1 + y2) / 2

    # Calculate the center of the frame
    frame_center_x = frame_width / 2
    frame_center_y = frame_height / 2

    # Calculate the distance between the box center and frame center
    distance_x = frame_center_x - box_center_x
    distance_y = frame_center_y - box_center_y

    return distance_x, distance_y

# Function to determine grid cell
def get_grid_cell(x1, y1, x2, y2, frame_width, frame_height, num_rows, num_cols):
    cell_width = frame_width / num_cols
    cell_height = frame_height / num_rows

    box_center_x = (x1 + x2) / 2
    box_center_y = (y1 + y2) / 2

    grid_col = int(box_center_x / cell_width)
    grid_row = int(box_center_y / cell_height)

    return grid_row, grid_col

# Function to draw grid lines
def draw_grid(frame, num_rows, num_cols):
    frame_height, frame_width = frame.shape[:2]
    print(frame.shape[:2],"hi")
    cell_width = int(frame_width / num_cols)
    cell_height = int(frame_height / num_rows)

    # Draw vertical lines
    for i in range(1, num_cols):
        x = i * cell_width
        cv2.line(frame, (x, 0), (x, frame_height), (255, 255, 255), 1)

    # Draw horizontal lines
    for j in range(1, num_rows):
        y = j * cell_height
        cv2.line(frame, (0, y), (frame_width, y), (255, 255, 255), 1)

# Function to draw bounding box and lines
def draw_bounding_box_and_lines(frame, x1, y1, x2, y2, distance_x, distance_y, grid_row, grid_col, num_rows, num_cols):
    # Draw bounding box
    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)    # Draw line from box center to frame center
    frame_width, frame_height = frame.shape[1], frame.shape[0]
    center_x, center_y = frame_width // 2, frame_height // 2

    cv2.line(frame, (int((x1 + x2) / 2), int((y1 + y2) / 2)), (center_x, center_y), (255, 0, 0), 2)

    # Draw lines indicating movements needed to position the object to the center
    cv2.line(frame, (center_x, center_y), (int((x1 + x2) / 2), int((y1 + y2) / 2)), (0, 0, 255), 2)

    # Draw text indicating distance, grid cell, and grid lines
    cv2.putText(frame, "Distance from Center: x={} cm, y={} cm".format(distance_x, distance_y), (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    cv2.putText(frame, "Grid Cell: ({}, {})".format(grid_row, grid_col), (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    draw_grid(frame, num_rows, num_cols)

# Function to process the webcam feed
def process_webcam_feed():
    cap = cv2.VideoCapture(0)

    # Known physical distance in centimeters
    known_physical_distance_cm = 50  # Replace with the known physical distance
    max_distance_limit_cm = 100  # Set the maximum allowed distance in centimeters

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        detected_boxes, detected_cls, detected_conf = detect_objects(frame)

        # Extract the detected objects and pass them to your CNN model
        for i in range(len(detected_boxes)):
            x1, y1, x2, y2 = detected_boxes[i]
            class_id = detected_cls[i]
            conf = detected_conf[i]

            if conf > 0.8 and conf < 0.88:
                # Calculate the distance from the center
                frame_width, frame_height = frame.shape[1], frame.shape[0]
                distance_x, distance_y = calculate_distance_from_center(x1, y1, x2, y2, frame_width, frame_height)

                # Limit the distance to the maximum allowed distance
                distance_x = max(-max_distance_limit_cm, min(distance_x, max_distance_limit_cm))
                distance_y = max(-max_distance_limit_cm, min(distance_y, max_distance_limit_cm))

                # Get grid cell
                grid_row, grid_col = get_grid_cell(x1, y1, x2, y2, frame_width, frame_height, num_rows, num_cols)

                # Convert pixel coordinates to cm using the known conversion factor
                pixels_per_cm_x = frame_width / known_physical_distance_cm
                pixels_per_cm_y = frame_height / known_physical_distance_cm
                print(pixels_per_cm_x)
                x1_cm, y1_cm, x2_cm, y2_cm = (
                    distance_x / pixels_per_cm_x,
                    distance_y / pixels_per_cm_y,
                    (distance_x + (x2 - x1)) / pixels_per_cm_x,
                    (distance_y + (y2 - y1)) / pixels_per_cm_y
                )

                # Print and display information
                print("Bounding Box Coordinates (in cm): x1={}, y1={}, x2={}, y2={}".format(x1_cm, y1_cm, x2_cm, y2_cm))
                print("Distance from Center (in cm): x={}, y={}".format(distance_x, distance_y))
                print("Grid Cell: ({}, {})".format(grid_row, grid_col))

                # Calculate direction to move
                direction_x = "left" if distance_x > 0 else "right"
                direction_y = "up" if distance_y > 0 else "down"

                print("Move {} and {}".format(direction_x, direction_y))

                # Draw bounding box, lines, and grid information
                draw_bounding_box_and_lines(frame, x1, y1, x2, y2, distance_x, distance_y, grid_row, grid_col, num_rows, num_cols)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Call the function to process the webcam feed
process_webcam_feed()
