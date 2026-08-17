import os
import numpy as np
import pandas as pd

# gesture mapping dictionary matching collection
gestures = {
    'thumbs_up': 0,
    'peace': 1,
    'heart': 2,
    'wave': 3,
    'fist': 4
}

# paths for raw and processed datasets
raw_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
processed_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')

# create processed directory if it doesn't exist
os.makedirs(processed_dir, exist_ok=True)

# normalizes 42 landmark coordinates (21 x,y points)
# 1. subtracts wrist (x0, y0) so wrist is relative origin (0, 0)
# 2. scales coordinates by max distance to make hand size uniform
def normalize_landmarks(landmarks):
    # reshape into (21, 2) x,y coordinate pairs
    coords = landmarks.reshape(-1, 2)
    
    # subtract wrist position (point 0)
    # every fingertip's coordinate is now relative to the wrist
    wrist = coords[0]
    rel_coords = coords - wrist
    
    # scale by max absolute value to keep points between -1.0 and 1.0
    # this makes the model invariant to hand size (whether hand was close or far from camera)
    max_val = np.max(np.abs(rel_coords))
    if max_val > 0:
        norm_coords = rel_coords / max_val
    else:
        norm_coords = rel_coords
        
    return norm_coords.flatten()

def main():
    X_data = []
    y_data = []

    print("\n--- starting data preprocessing ---")

    # loop through each gesture folder and read saved .npy files
    for gesture_name, label in gestures.items():
        folder_path = os.path.join(raw_dir, gesture_name)
        if not os.path.exists(folder_path):
            print(f"warning: folder {gesture_name} not found.")
            continue

        files = [f for f in os.listdir(folder_path) if f.endswith('.npy')]
        print(f"processing {len(files)} samples for gesture: '{gesture_name}' (label: {label})")

        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            landmarks = np.load(file_path)

            if len(landmarks) == 42:
                normalized = normalize_landmarks(landmarks)
                X_data.append(normalized)
                y_data.append(label) # 0 -> thumbs_up, 1 -> peace, etc.

                # frontend will later map these string labels to emojis + text for display

    # convert to pandas DataFrames
    df_X = pd.DataFrame(X_data)
    df_y = pd.DataFrame(y_data, columns=['label'])

    # save processed datasets to csv
    landmarks_csv_path = os.path.join(processed_dir, 'landmarks.csv')
    labels_csv_path = os.path.join(processed_dir, 'labels.csv')

    df_X.to_csv(landmarks_csv_path, index=False)
    df_y.to_csv(labels_csv_path, index=False)

    print(f"\nsuccess! dataset saved:")
    print(f" - features: {landmarks_csv_path} ({df_X.shape[0]} rows, {df_X.shape[1]} columns)")
    print(f" - labels  : {labels_csv_path} ({df_y.shape[0]} rows)\n")

if __name__ == '__main__':
    main()
