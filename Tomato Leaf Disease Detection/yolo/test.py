# from ultralytics import YOLO
# model=YOLO('best.pt')
# model.predict(source=0,imgsz=640,conf=0.6,show=True)
# Import libraries
# import cv2
# import numpy as np
# import torch
# from ultralytics import YOLO

# # Load the image
# img = cv2.imread(r'C:\Users\ramesh\Desktop\mainproject\crop disease\object detection\th.jpg')

# Load the model
# from ultralytics import YOLO

# # Load a model
# model = YOLO('best.pt')  # pretrained YOLOv8n model

# # Run inference on a single image
# results = model.predict(source=r'C:\Users\ramesh\Desktop\mainproject\crop disease\object detection\th.jpg', save=True, project='output', name='result')
# # Access results attributes
# boxes = results[0].boxes  # Boxes object for bounding box outputs
# masks = results[0].masks  # Masks object for segmentation masks outputs
# keypoints = results[0].keypoints  # Keypoints object for pose outputs
# probs = results[0].probs# Probs object for classification outputs
# # results.show()  # display to screen
# # results.save(filename='result.jpg')  # save to file
# # save to disk
from ultralytics import YOLO
import cv2

# Load a model
model = YOLO('best.pt')  # pretrained YOLOv8n model

# Run inference on a single image
results = model.predict(source=r'C:\Users\ramesh\Desktop\mainproject\crop disease\object detection\th.jpg', save=False)

# Access results attributes
boxes = results[0].boxes  # Boxes object for bounding box outputs

# Load the image
img = cv2.imread(r'C:\Users\ramesh\Desktop\mainproject\crop disease\object detection\th.jpg')

# Crop and save each detected object
for i, box in enumerate(boxes.xyxy):
    x1, y1, x2, y2 = box
    # Convert coordinates to integers
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    # Crop the detected object
    cropped_object = img[y1:y2, x1:x2]
    # Save the cropped object to disk
    cv2.imwrite(f'cropped_object_{i}.jpg', cropped_object)
    print(f"Object {i+1} cropped and saved successfully.")

print("All objects cropped and saved successfully.")
