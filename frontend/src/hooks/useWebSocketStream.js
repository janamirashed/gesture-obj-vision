import { useState, useEffect, useRef } from 'react';

export function useWebSocketStream(videoRef, enabled = true) {
  const [gestures, setGestures] = useState([]);
  const [objects, setObjects] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [fps, setFps] = useState(0);

  const socketRef = useRef(null);
  const isProcessingRef = useRef(false);
  const frameCountRef = useRef(0);
  const lastFpsTimeRef = useRef(Date.now());

  useEffect(() => {
    if (!enabled) return;

    // downscaled capture canvas for high-speed transmission (480x360)
    const captureCanvas = document.createElement('canvas');
    const captureCtx = captureCanvas.getContext('2d');
    captureCanvas.width = 480;
    captureCanvas.height = 360;

    // connect to fastapi backend websocket server
    const ws = new WebSocket('ws://localhost:8000/ws/stream');
    socketRef.current = ws;

    const sendNextFrame = () => {
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      if (!videoRef.current || videoRef.current.readyState < 2) {
        setTimeout(sendNextFrame, 50);
        return;
      }

      if (isProcessingRef.current) return;
      isProcessingRef.current = true;

      const video = videoRef.current;
      captureCtx.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);
      const base64Image = captureCanvas.toDataURL('image/jpeg', 0.5);

      ws.send(base64Image);
    };

    ws.onopen = () => {
      console.log('connected to gesture vision websocket server');
      setIsConnected(true);
      isProcessingRef.current = false;
      sendNextFrame();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setGestures(data.gestures || []);
        setObjects(data.objects || []);

        // calculate live fps
        frameCountRef.current += 1;
        const now = Date.now();
        if (now - lastFpsTimeRef.current >= 1000) {
          setFps(frameCountRef.current);
          frameCountRef.current = 0;
          lastFpsTimeRef.current = now;
        }
      } catch (err) {
        console.error('error parsing websocket response:', err);
      } finally {
        // unlock processing flag and request next frame immediately for zero lag
        isProcessingRef.current = false;
        requestAnimationFrame(sendNextFrame);
      }
    };

    ws.onclose = () => {
      console.log('disconnected from websocket server');
      setIsConnected(false);
      isProcessingRef.current = false;
    };

    ws.onerror = (err) => {
      console.error('websocket error:', err);
      isProcessingRef.current = false;
    };

    return () => {
      if (ws) ws.close();
    };
  }, [videoRef, enabled]);

  return { gestures, objects, isConnected, fps };
}
