import os
import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp

# maps target class indices to gesture names
gestures = {
    0: 'thumbs_up',
    1: 'peace',
    2: 'heart',
    3: 'wave',
    4: 'fist'
}

class GestureDetector:
    def __init__(self, model_path=None):
        # set default path to trained keras gesture model
        if model_path is None:
            model_path = os.path.join(
                os.path.dirname(__file__), '..', 'model', 'saved_models', 'gesture_classifier.keras'
            )
        
        # load trained keras model to pass inputs through
        self.model = tf.keras.models.load_model(model_path)

        # initialize mediapipe hand detector
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def normalize_landmarks(self, landmarks):
        # reshape 42 values to 21 x,y coordinate pairs
        coords = landmarks.reshape(-1, 2)
        
        # subtract wrist position (point 0) so wrist is relative origin (0,0)
        wrist = coords[0]
        rel_coords = coords - wrist
        
        # scale coordinates by max distance to make hand size uniform
        max_val = np.max(np.abs(rel_coords))
        if max_val > 0:
            norm_coords = rel_coords / max_val
        else:
            norm_coords = rel_coords

        return norm_coords.flatten()

    def predict(self, frame):
        # convert bgr camera frame to rgb for mediapipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        gesture_results = []

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # extract 21 joint x,y coordinates
                all_coords = []
                for lm in hand_landmarks.landmark:
                    all_coords.extend([lm.x, lm.y])
                
                raw_landmarks = np.array(all_coords, dtype=np.float32)
                norm_landmarks = self.normalize_landmarks(raw_landmarks)

                # predict gesture probabilities with trained model
                # input is the 42 normalized landmarks
                # output is the gesture class probabilities (for each gesture)
                input_data = np.expand_dims(norm_landmarks, axis=0)
                predictions = self.model.predict(input_data, verbose=0)[0]
                
                # get gesture name with highest probability
                class_id = int(np.argmax(predictions)) # outputs index of the max probability (0-4)
                confidence = float(predictions[class_id]) # converts probability (a tf value) to a float
                gesture_name = gestures.get(class_id, 'unknown') # maps the index to the gesture name

                gesture_results.append({
                    'gesture': gesture_name,
                    'confidence': round(confidence, 2),
                    'landmarks': [[lm.x, lm.y] for lm in hand_landmarks.landmark] # for visualization
                })

        return gesture_results

if __name__ == '__main__':
    # test gesture detector on a blank frame
    detector = GestureDetector()
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    results = detector.predict(dummy_frame)
    print("gesture detector initialized successfully! test frame result:", results)
