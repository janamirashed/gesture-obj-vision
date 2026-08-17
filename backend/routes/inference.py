import sys
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# add project root to python path for detection imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.video import decode_base64_frame
from detection.gesture_detector import GestureDetector
from detection.object_detector import ObjectDetector

router = APIRouter()

# initialize detectors for rest endpoints
gesture_detector = GestureDetector()
object_detector = ObjectDetector()

class PredictRequest(BaseModel):
    image: str # base64 image string

@router.post("/api/predict")
async def predict_single_frame(request: PredictRequest):
    # decode base64 image
    # for snapshots/still images to test using postman
    frame = decode_base64_frame(request.image)
    if frame is None:
        raise HTTPException(status_code=400, detail="invalid image data")

    # run gesture detection and object detection
    gestures = gesture_detector.predict(frame)
    objects = object_detector.detect(frame, conf_threshold=0.5)

    return {
        "status": "success",
        "gestures": gestures,
        "objects": objects
    }
