import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# add backend directory to sys.path
sys.path.append(os.path.dirname(__file__))

from routes.stream import router as stream_router
from routes.inference import router as inference_router

app = FastAPI(title="Gesture & Object Vision API")

# configure cors middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include websocket and rest routes
app.include_router(stream_router)
app.include_router(inference_router)

@app.get("/")
def root():
    return {"status": "online", "message": "Gesture & Object Vision API is running"}

if __name__ == '__main__':
    # pyrefly: ignore [missing-import]
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # for auto-reloading on changes

