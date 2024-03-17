import cv2
import numpy as np
from ultralytics import YOLO
import tensorflow as tf

# Load YOLOv5
model = YOLO(r'C:\Users\ramesh\Desktop\mainproject\Object Detection\yolov8 tomoto\best.pt')
# names=["tomato","not tomato"]
cnn_model = tf.keras.models.load_model('cnn/tomato_255_32_cnn.h5')
names=['ripe','ripe','ripe','unripe']

# Function to detect objects using YOLOv
def detect_objects(frame):
    results = model(frame)
    detected_boxes, detected_cls, detected_conf = [], [], []
    for result in results:
        boxes = result.boxes.xyxy  # get box coordinates in (top, left, bottom, right) format
        conf = result.boxes.conf   # confidence scores
        cls = result.boxes.cls 
        for i in range(len(boxes)):
            if conf[i] > 0.8 and conf[i] <0.88 :
                detected_boxes.append(boxes[i])
                detected_cls.append(cls[i])
                detected_conf.append(conf[i])
    return detected_boxes, detected_cls, detected_conf

# Function to process the webcam feed
def process_webcam_feed():
    cap = cv2.VideoCapture(0)
    
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
                print(conf)
       
                if conf > 0.8 and conf < 0.88:
                        print("Bounding Box Coordinates: x1={}, y1={}, x2={}, y2={}".format(x1, y1, x2, y2))
                        print("AREA POINT: ", (abs(x2-x1)*abs(y2-y1)))
                        
                        tomato = frame[int(y1):int(y2), int(x1):int(x2)]
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 0), 2)
                        
                        # Preprocess tomato image before passing it to your CNN model
                        # Assuming your CNN model expects a certain input size, adjust the size of the tomato accordingly
                        your_expected_width, your_expected_height = 255, 255 # Adjust as needed
                        tomato = cv2.resize(tomato, (your_expected_width, your_expected_height))
                        output_path = r'C:\Users\ramesh\Desktop\mainproject\Object Detection\Tomato\resized_tomato.jpg' 
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
                        
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    cap.release()
    cv2.destroyAllWindows()

# Call the function to process the webcam feed
process_webcam_feed()

