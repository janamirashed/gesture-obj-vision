import React, { useState, useEffect, useRef } from 'react';
import { useWebSocketStream } from './hooks/useWebSocketStream';
import { drawDetections } from './utils/drawCanvas';

const GESTURES = [
  { id: 'thumbs_up', label: 'thumbs up', emoji: '👍' },
  { id: 'peace', label: 'peace', emoji: '✌️' },
  { id: 'heart', label: 'heart', emoji: '🫶' },
  { id: 'wave', label: 'wave', emoji: '👋' },
  { id: 'fist', label: 'fist', emoji: '✊' },
];

const PLACEHOLDER_GESTURE = {
  id: 'none',
  label: 'show hand',
  emoji: '✋'
};

const OBJECT_EMOJIS = {
  'cell phone': '📱',
  'cup': '☕',
  'laptop': '💻',
  'book': '📖',
  'bottle': '🍾',
  'person': '👤',
  'chair': '🪑',
  'mouse': '🖱️',
  'keyboard': '⌨️',
};

const IOSEmoji = ({ emoji, size = 'sm' }) => (
  <img
    src={`https://emojicdn.elk.sh/${encodeURIComponent(emoji)}?style=apple`}
    alt={emoji}
    className={size === 'lg' ? 'ios-emoji-lg' : 'ios-emoji-sm'}
    loading="lazy"
  />
);

export default function App() {
  const [activeGesture, setActiveGesture] = useState('none');
  const [confidence, setConfidence] = useState(0);
  const [detectedObjects, setDetectedObjects] = useState([
    { name: 'cell phone', confidence: 92, emoji: '📱' },
    { name: 'cup', confidence: 88, emoji: '☕' },
  ]);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  
  // gesture history queue for stabilization (debouncing)
  const gestureHistoryRef = useRef([]);
  const noHandCounterRef = useRef(0);

  // connect real-time websocket stream to fastapi backend
  const { gestures, objects, isConnected, fps } = useWebSocketStream(videoRef);

  useEffect(() => {
    // start local webcam for feed
    async function setupCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { width: 640, height: 480 } 
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.warn('Webcam permission pending or not available:', err);
      }
    }
    setupCamera();
  }, []);

  // gesture stabilization (debouncing) + placeholder handling when no hand detected
  useEffect(() => {
    if (gestures && gestures.length > 0) {
      const topGesture = gestures[0];
      
      if (topGesture.gesture && topGesture.gesture !== 'unknown' && topGesture.confidence >= 0.65) {
        noHandCounterRef.current = 0;
        const history = gestureHistoryRef.current;
        history.push(topGesture);
        if (history.length > 6) history.shift();

        // count occurrences of each gesture in recent frame history
        const counts = {};
        history.forEach(item => {
          counts[item.gesture] = (counts[item.gesture] || 0) + 1;
        });

        // find most frequent gesture in history
        let maxGesture = null;
        let maxCount = 0;
        Object.entries(counts).forEach(([gName, count]) => {
          if (count > maxCount) {
            maxCount = count;
            maxGesture = gName;
          }
        });

        // update active gesture if held consistently for 4+ consecutive frames
        if (maxGesture && maxCount >= 4) {
          setActiveGesture(maxGesture);
          setConfidence(Math.round(topGesture.confidence * 100));
        }
      } else {
        handleNoHandDetected();
      }
    } else {
      handleNoHandDetected();
    }

    function handleNoHandDetected() {
      noHandCounterRef.current += 1;
      // if no valid hand detected for 8 consecutive frames (~0.3s), reset to placeholder
      if (noHandCounterRef.current >= 8) {
        gestureHistoryRef.current = [];
        setActiveGesture('none');
        setConfidence(0);
      }
    }
  }, [gestures]);

  // update detected objects when live yolo predictions arrive
  useEffect(() => {
    if (objects && objects.length > 0) {
      const formattedObjects = objects.map(obj => ({
        name: obj.name,
        confidence: Math.round(obj.confidence * 100),
        emoji: OBJECT_EMOJIS[obj.name] || '📦'
      }));
      setDetectedObjects(formattedObjects);
    }
  }, [objects]);

  // draw yolo bounding boxes onto overlay canvas
  useEffect(() => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;

      drawDetections(canvas, gestures, objects, { showSkeleton: false, showBoxes: true });
    }
  }, [gestures, objects]);

  const currentGestureObj = GESTURES.find(g => g.id === activeGesture) || PLACEHOLDER_GESTURE;

  return (
    <div className="app-wrapper">
      {/* top header — read-only AI gesture status chips + server status pill */}
      <header className="top-header">
        <div className="gesture-chips">
          {GESTURES.map((g) => (
            <div
              key={g.id}
              className={`chip ${activeGesture === g.id ? 'active' : ''}`}
            >
              <IOSEmoji emoji={g.emoji} size="sm" />
              <span>{g.label}</span>
            </div>
          ))}
        </div>

        {/* server status pill */}
        <div className="status-bar">
          <span className={`status-dot ${isConnected ? 'online' : 'offline'}`}></span>
          <span className="status-text">{isConnected ? `Live (${fps} FPS)` : 'Connecting...'}</span>
        </div>
      </header>

      {/* main content grid */}
      <main className="main-grid">
        {/* left: camera viewfinder card */}
        <div className="camera-card">
          <div className="video-container">
            {/* mirrored webcam video */}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="webcam-video"
            />

            {/* real-time canvas overlay for bounding boxes */}
            <canvas
              ref={canvasRef}
              className="overlay-canvas"
            />

            {/* bottom floating detection badge */}
            <div className="detection-pill">
              <span className="dot-indicator"></span>
              <span>
                {activeGesture !== 'none' 
                  ? `detected: ${currentGestureObj.label} (${confidence}%)`
                  : 'awaiting hand gesture...'
                }
              </span>
            </div>
          </div>

          <p className="camera-caption">
            show a hand to the camera &middot; hold the gesture for ~0.3s
          </p>
        </div>

        {/* right: ai output display with card stack hover transition & placeholder state */}
        <div className="result-card">
          <div className="card-stack-wrapper" key={activeGesture}>
            <div className={`result-image-wrapper ${activeGesture === 'none' ? 'placeholder' : ''}`}>
              <IOSEmoji emoji={currentGestureObj.emoji} size="lg" />
            </div>

            {/* handwriting sticker */}
            <div className={`sticker-badge ${activeGesture === 'none' ? 'placeholder' : ''}`}>
              <span>{currentGestureObj.label}</span>
              <IOSEmoji emoji={currentGestureObj.emoji} size="sm" />
            </div>
          </div>

          {/* detected objects section */}
          <div className="objects-section">
            <span className="objects-title">Detected Objects</span>
            <div className="objects-list">
              {detectedObjects.map((obj, idx) => (
                <div key={idx} className="object-chip">
                  <IOSEmoji emoji={obj.emoji} size="sm" />
                  <span>{obj.name} ({obj.confidence}%)</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
