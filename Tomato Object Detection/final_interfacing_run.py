import cv2
import numpy as np
from ultralytics import YOLO
import tensorflow as tf
import os

import serial
import time
x_check = 0
y_check = 0
x_sent = 0
y_sent = 0
count = 0
bluetooth=serial.Serial("/dev/rfcomm0",9600)   #Device 00:00:13:00:4E:6A Name: HC-05

def bluetooth_comm(x, y):
    global x_check, y_check, count
    if (abs(x_check - x) < 1) or (abs(y_check - y) < 1):
        count = count + 1
    else:
        count = 0
    x_check = x
    y_check = y

    if count == 5:
        x = int(x * 100)
        y = int(y * 100)
        global x_sent, y_sent
        if (abs(x_sent - x) > 10) or (abs(y_sent - y) > 10):
            string='X{0}'.format(x)
            bluetooth.write(string.encode("utf-8"))
            print('Sent to HC-05 ', string)
            x_sent = x
            time.sleep(2)
            string='Y{0}'.format(y)
            bluetooth.write(string.encode("utf-8"))
            print('Sent to HC-05 ', string)
            y_sent = y
        count = 0

# Load YOLOv5
model = YOLO('yolo tomoto/tomato_yolo_30e_97a.pt')
cnn_model = tf.keras.models.load_model('path/to/tomato_255p_cnn_32e_a.h5')  # available in the drive link in the readme file
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
        # get box coordinates in (top, left, bottom, right) format
        boxes = result.boxes.xyxy
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
    print(frame.shape[:2], "hi")
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
    # Draw line from box center to frame center
    cv2.rectangle(frame, (int(x1), int(y1)),
                  (int(x2), int(y2)), (0, 255, 0), 2)
    frame_width, frame_height = frame.shape[1], frame.shape[0]
    center_x, center_y = frame_width // 2, frame_height // 2

    cv2.line(frame, (int((x1 + x2) / 2), int((y1 + y2) / 2)),
             (center_x, center_y), (255, 0, 0), 2)

    # Draw lines indicating movements needed to position the object to the center
    cv2.line(frame, (center_x, center_y),
             (int((x1 + x2) / 2), int((y1 + y2) / 2)), (0, 0, 255), 2)

    # Draw text indicating distance, grid cell, and grid lines
    cv2.putText(frame, "Distance from Center: x={} cm, y={} cm".format(distance_x, distance_y), (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    cv2.putText(frame, "Grid Cell: ({}, {})".format(grid_row, grid_col), (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    draw_grid(frame, num_rows, num_cols)

# Function to calculate distance in pixels
def calculate_distance_in_pixels(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) * 2 + (y2 - y1) * 2)

# Function to convert pixels to centimeters
def pixels_to_cm(pixels, cm_per_pixel):
    return pixels * cm_per_pixel

# Function to process the webcam feed
def process_webcam_feed():
    cap = cv2.VideoCapture(0)

    # Known physical distance in centimeters
    known_physical_distance_cm = 50  # Replace with the known physical distance
    max_distance_limit_cm = 100  # Set the maximum allowed distance in centimeters

    closest_tomato_bbox = None  # Initialize variable to store closest tomato bounding box

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Get pixel values of the frame
        frame_height, frame_width = frame.shape[:2]

        detected_boxes, detected_cls, detected_conf = detect_objects(frame)

        min_distance = float('inf')  # Initialize with a large value
        closest_tomato_index = -1

        # Extract the detected objects and pass them to your CNN model
        for i in range(len(detected_boxes)):
            x1, y1, x2, y2 = detected_boxes[i]
            class_id = detected_cls[i]
            conf = detected_conf[i]

            if conf > 0.8 and conf < 0.88:
                # Calculate the distance from the center
                frame_width, frame_height = frame.shape[1], frame.shape[0]
                distance_x, distance_y = calculate_distance_from_center(
                    x1, y1, x2, y2, frame_width, frame_height)

                # Calculate Euclidean distance from the center
                distance_from_center = np.sqrt(
                    distance_x * 2 + distance_y * 2)

                if distance_from_center < min_distance:
                    min_distance = distance_from_center
                    closest_tomato_index = i

                    # Store the bounding box coordinates of the closest tomato
                    closest_tomato_bbox = (x1, y1, x2, y2)

                # Limit the distance to the maximum allowed distance
                distance_x = max(-max_distance_limit_cm,
                                 min(distance_x, max_distance_limit_cm))
                distance_y = max(-max_distance_limit_cm,
                                 min(distance_y, max_distance_limit_cm))

                # Get grid cell
                grid_row, grid_col = get_grid_cell(
                    x1, y1, x2, y2, frame_width, frame_height, num_rows, num_cols)

                # Convert pixel coordinates to cm using the known conversion factor
                pixels_per_cm_x = frame_width / known_physical_distance_cm
                pixels_per_cm_y = frame_height / known_physical_distance_cm

                x1_cm, y1_cm, x2_cm, y2_cm = (
                    distance_x / pixels_per_cm_x,
                    distance_y / pixels_per_cm_y,
                    (distance_x + (x2 - x1)) / pixels_per_cm_x,
                    (distance_y + (y2 - y1)) / pixels_per_cm_y
                )
                
                # Print and display information
                direction_x = "left" if distance_x > 0 else "right"
                direction_y = "up" if distance_y > 0 else "down"

                print("Move {} and {}".format(direction_x, direction_y))
                
                frame_center_x, frame_center_y = frame_width // 2, frame_height // 2
                box_center_x, box_center_y = (x1 + x2) / 2, (y1 + y2) / 2

                # Calculate distance in pixels
                distance_x_pixels = abs(frame_center_x - box_center_x)
                distance_y_pixels = abs(frame_center_y - box_center_y)

                # Convert pixels to centimeters
                cm_per_pixel_x = grid_width_cm / 213.33
                cm_per_pixel_y = grid_height_cm / 160

                distance_x_cm = pixels_to_cm(
                    distance_x_pixels, cm_per_pixel_x) * (-1 if direction_x == "left" else 1)
                distance_y_cm = pixels_to_cm(
                    distance_y_pixels, cm_per_pixel_y) * (-1 if direction_y == "down" else 1)


                # Take the closest tomato bounding box
                tomato = frame[int(y1):int(y2), int(x1):int(x2)]
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 0), 2)

                # Preprocess tomato image before passing it to your CNN model
                your_expected_width, your_expected_height = 255, 255 # Adjust as needed
                tomato = cv2.resize(tomato, (your_expected_width, your_expected_height))
                output_path = 'detected_tomatoes/resized_tomato.jpg' 
                # Replace with your desired output path and file name
                cv2.imwrite(output_path, tomato)
                
                # Preprocess the tomato image as needed by your CNN model
                # Make a prediction using your CNN model
                image = tf.keras.preprocessing.image.load_img(output_path,target_size=(255,255))
                input_arr = tf.keras.preprocessing.image.img_to_array(image)
                input_arr = np.array([input_arr])  # Convert single image to a batch.
                predictions = cnn_model.predict(input_arr)

                print(predictions)

                result_index = np.argmax(predictions) #Return index of max element
                print(names[result_index])
                if names[result_index] == 'ripe':
                    print("Distance of ripe tomato from center: \nx = {} cm \ny = {} cm".format(distance_x_cm, distance_y_cm))
                    bluetooth_comm(distance_x_cm, distance_y_cm)
                else:
                    print("Unripe tomato")

        # After looping through all detected tomatoes, color the closest one green and the rest red
        for i in range(len(detected_boxes)):
            x1, y1, x2, y2 = detected_boxes[i]
            if i == closest_tomato_index:
                color = (0, 255, 0)  # Green for closest tomato
            else:
                color = (0, 0, 255)  # Red for other tomatoes
            cv2.rectangle(frame, (int(x1), int(y1)),
                          (int(x2), int(y2)), color, 2)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # After the loop ends, store the closest tomato bounding box coordinates
    # if closest_tomato_bbox:
    #     with open('closest_tomato_bbox.txt', 'w') as file:
    #         file.write(','.join(map(str, closest_tomato_bbox)))

# Call the function to process the webcam feed
process_webcam_feed()