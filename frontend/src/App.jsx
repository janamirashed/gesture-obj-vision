import React, { useState, useEffect, useRef } from 'react';

const GESTURES = [
  { id: 'thumbs_up', label: 'thumbs up', emoji: '👍' },
  { id: 'peace', label: 'peace', emoji: '✌️' },
  { id: 'heart', label: 'heart', emoji: '🫶' },
  { id: 'wave', label: 'wave', emoji: '👋' },
  { id: 'fist', label: 'fist', emoji: '✊' },
];

const IOSEmoji = ({ emoji, size = 'sm' }) => (
  <img
    src={`https://emojicdn.elk.sh/${encodeURIComponent(emoji)}?style=apple`}
    alt={emoji}
    className={size === 'lg' ? 'ios-emoji-lg' : 'ios-emoji-sm'}
    loading="lazy"
  />
);

export default function App() {
  const [activeGesture, setActiveGesture] = useState('peace');
  const [confidence, setConfidence] = useState(94);
  const [detectedObjects, setDetectedObjects] = useState([
    { name: 'cell phone', confidence: 92, emoji: '📱' },
    { name: 'cup', confidence: 88, emoji: '☕' },
  ]);

  const videoRef = useRef(null);

  useEffect(() => {
    // start local webcam for feed demo
    async function setupCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.warn('Webcam permission pending or not available:', err);
      }
    }
    setupCamera();
  }, []);

  const currentGestureObj = GESTURES.find(g => g.id === activeGesture) || GESTURES[1];

  return (
    <div className="app-wrapper">
      {/* top header — centered chips */}
      <header className="top-header">
        <div className="gesture-chips">
          {GESTURES.map((g) => (
            <button
              key={g.id}
              className={`chip ${activeGesture === g.id ? 'active' : ''}`}
              onClick={() => setActiveGesture(g.id)}
            >
              <IOSEmoji emoji={g.emoji} size="sm" />
              <span>{g.label}</span>
            </button>
          ))}
        </div>
      </header>

      {/* main content grid */}
      <main className="main-grid">
        {/* left: camera viewfinder card */}
        <div className="camera-card">
          <div className="video-container">
            {/* top progress line */}
            <div className="progress-bar-container">
              <div className="progress-fill" style={{ width: `${confidence}%` }}></div>
            </div>

            {/* mirrored webcam video */}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="webcam-video"
            />

            {/* bottom floating detection badge */}
            <div className="detection-pill">
              <span className="dot-indicator"></span>
              <span>detected: <IOSEmoji emoji={currentGestureObj.emoji} size="sm" /> {currentGestureObj.label} ({confidence}%)</span>
            </div>
          </div>

          <p className="camera-caption">
            show a hand to the camera &middot; hold the gesture for ~0.7s
          </p>
        </div>

        {/* right: ai output display & objects card */}
        <div className="result-card">
          <div className="result-image-wrapper">
            <IOSEmoji emoji={currentGestureObj.emoji} size="lg" />
          </div>

          {/* handwriting sticker */}
          <div className="sticker-badge">
            <span>{currentGestureObj.label}</span>
            <IOSEmoji emoji={currentGestureObj.emoji} size="sm" />
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
