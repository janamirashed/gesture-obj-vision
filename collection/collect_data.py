import cv2
import mediapipe as mp
import numpy as np
import os
import time

# defining gestures for data collection
gestures = {
    '0': 'thumbs_up',
    '1': 'peace',
    '2': 'heart',
    '3': 'wave',
    '4': 'fist'
}

# path to save raw dataset samples
save_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')

# create subfolders for each gesture
for gesture in gestures.values():
    os.makedirs(os.path.join(save_path, gesture), exist_ok=True)

# initialize mediapipe hand tracking
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,       
    min_detection_confidence=0.7, # must be atleast 70% confident for hand to be detected (to avoid false positives)
    min_tracking_confidence=0.7 # must be atleast 70% confident for hand to be tracked
)

# used for tracking data collection progress
# saves each gesture to its assigned folder (automatic labelling while collection)
def get_sample_counts():
    counts = {}
    for gesture in gestures.values():
        folder = os.path.join(save_path, gesture)
        os.makedirs(folder, exist_ok=True)
        counts[gesture] = len(os.listdir(folder))

    return counts

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("error: could not open webcam.")
        return

    current_gesture_key = '0'
    recording = False
    last_save_time = 0
    save_interval = 0.15 # save 1 sample every 150 ms -> 6-7 samples per second

    print("\n--- gesture data collector ---")
    print("keys 0-4: select gesture | space: toggle record | s: snapshot | q: quit\n")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("error: failed to capture frame.")
            break

        # flip frame for mirror view (as if we're looking in a mirror)
        # this is done for consistency with real world use
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # draw hand landmarks on frame
        results = hands.process(frame_rgb)

        current_gesture = gestures[current_gesture_key]
        counts = get_sample_counts()
        landmarks_vector = None

        # if hands detected, draw landmarks and save sample
        if results.multi_hand_landmarks:
            all_coords = []
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                for lm in hand_landmarks.landmark:
                    all_coords.extend([lm.x, lm.y]) # normalized coordinates for model to work on any screen resoltuion

            if len(all_coords) >= 42:
                landmarks_vector = np.array(all_coords[:42], dtype=np.float32)

        # save landmarks every save_interval ms if recording
        # save with timestamp to avoid duplicates in assigned folders
        now = time.time()
        if recording and landmarks_vector is not None:
            if now - last_save_time >= save_interval:
                timestamp = int(now * 1000)
                file_path = os.path.join(save_path, current_gesture, f"sample_{timestamp}.npy")
                np.save(file_path, landmarks_vector)
                last_save_time = now

        # on-screen video overlay
        rec_color = (0, 255, 0) if recording else (255, 255, 255)
        status_text = f"active: {current_gesture.upper()} [{counts[current_gesture]} saved]"
        rec_text = "recording..." if recording else "idle [press space]"

        cv2.rectangle(frame, (10, 10), (480, 95), (20, 20, 20), -1)
        cv2.putText(frame, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, rec_text, (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, rec_color, 2)

        cv2.imshow("gestureVision - data collector", frame)

        # keyboard listener
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif chr(key) in gestures:
            current_gesture_key = chr(key)
        elif key == ord(' '):
            recording = not recording
        elif key == ord('s') and landmarks_vector is not None:
            timestamp = int(now * 1000)
            file_path = os.path.join(save_path, current_gesture, f"sample_{timestamp}.npy")
            np.save(file_path, landmarks_vector)

    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == '__main__':
    main()