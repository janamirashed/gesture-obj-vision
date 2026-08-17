import sys
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# add project root to python path for detection imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.video import decode_base64_frame
from detection.gesture_detector import GestureDetector
from detection.object_detector import ObjectDetector

router = APIRouter()

# initialize detectors once when server module loads
gesture_detector = GestureDetector()
object_detector = ObjectDetector()

@router.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    # accept incoming websocket connection from frontend
    await websocket.accept()
    print("websocket client connected")

    try:
        while True:
            # receive base64 encoded frame string from react
            data = await websocket.receive_text()
            frame = decode_base64_frame(data)

            if frame is None:
                continue

            # run gesture detection and object detection on current frame
            gestures = gesture_detector.predict(frame)
            objects = object_detector.detect(frame, conf_threshold=0.5)

            # send combined json response back to react
            await websocket.send_json({
                "gestures": gestures,
                "objects": objects
            })

    except WebSocketDisconnect:
        print("websocket client disconnected")

# notes

# 1. websocket connection allows bi-directional continuous streaming without http overhead per frame
# 2. detectors are initialized once at router level so neural networks stay loaded in memory
# 3. try/except WebSocketDisconnect handles graceful disconnection when user closes browser tab
