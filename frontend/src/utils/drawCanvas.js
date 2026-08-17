export function drawDetections(canvas, gestures = [], objects = [], options = { showSkeleton: false, showBoxes: true }) {
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const { width, height } = canvas;

  // clear canvas before re-drawing
  ctx.clearRect(0, 0, width, height);

  // 1. hand skeleton joint lines (disabled per user preference)
  if (options.showSkeleton && gestures) {
    // disabled for clean camera aesthetic
  }

  // 2. draw yolo object bounding boxes and readable text labels
  if (options.showBoxes && objects) {
    objects.forEach((obj) => {
      if (!obj.box) return;
      const [nx1, ny1, nx2, ny2] = obj.box;
      
      // mirror x coordinates so bounding boxes align pixel-perfectly with mirrored webcam video
      const x1 = (1 - nx2) * width;
      const x2 = (1 - nx1) * width;
      const y1 = ny1 * height;
      const y2 = ny2 * height;
      const boxWidth = x2 - x1;
      const boxHeight = y2 - y1;

      // draw bounding box rect
      ctx.strokeStyle = '#a855f7';
      ctx.lineWidth = 2.5;
      ctx.strokeRect(x1, y1, boxWidth, boxHeight);

      // draw label badge background
      const label = `${obj.name} ${Math.round(obj.confidence * 100)}%`;
      ctx.font = 'bold 12px Inter, sans-serif';
      const textWidth = ctx.measureText(label).width;

      ctx.fillStyle = 'rgba(168, 85, 247, 0.85)';
      ctx.fillRect(x1, y1 > 22 ? y1 - 22 : y1, textWidth + 10, 20);

      // draw label text
      ctx.fillStyle = '#ffffff';
      ctx.fillText(label, x1 + 5, y1 > 22 ? y1 - 7 : y1 + 14);
    });
  }
}
