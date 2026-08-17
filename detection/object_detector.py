import cv2
from ultralytics import YOLO


class ObjectDetector:
    # yolo11m.pt (medium model, 20M params) provides state-of-the-art accuracy for everyday objects
    def __init__(self, model_name="yolo11m.pt"):
        self.model = YOLO(model_name)

    # method takes in a frame & confidence level to filter out uncertain detections
    def detect(self, frame, conf_threshold=0.3):
        h, w = frame.shape[:2]

        # convert OpenCV BGR frame to RGB for neural network color accuracy
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = self.model(rgb_frame, conf=conf_threshold, verbose=False)[0]
        
        detections = []
        
        # loop through detected objects & extract info
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist() # bounding box coords
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            label = self.model.names[class_id]

            # store detection + accuracy + normalized [0..1] box coords
            detections.append({
                'name': label,
                'confidence': round(confidence, 2),
                'box': [round(x1 / w, 4), round(y1 / h, 4), round(x2 / w, 4), round(y2 / h, 4)]
            })
        return detections

if __name__ == '__main__':
    # test object detector 
    import numpy as np
    detector = ObjectDetector()
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    results = detector.detect(dummy_frame, conf_threshold=0.3)

    print("object detector initialized successfully! detected objects in test frame:", results)