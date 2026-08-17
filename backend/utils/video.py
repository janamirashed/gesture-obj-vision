import base64
import cv2
import numpy as np

# decodes base64 string from frontend into opencv bgr frame
def decode_base64_frame(base64_string: str) -> np.ndarray:
    # strip base64 header if present (e.g. 'data:image/jpeg;base64,')
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]

    # decode base64 string to image bytes
    image_bytes = base64.b64decode(base64_string)

    # convert raw bytes to 1d unsigned 8-bit integer numpy array
    np_arr = np.frombuffer(image_bytes, np.uint8)

    # decode 1d array into 3d opencv bgr numpy matrix (height x width x 3)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    return frame

# notes

# 1. react canvas captures webcam frames as base64 strings (text format suitable for websocket transmission)
# 2. base64 strings contain a prefix header (data:image/jpeg;base64,) which must be stripped before decoding
# 3. cv2.imdecode converts raw binary image bytes into a 3d bgr array required by mediapipe & yolo
