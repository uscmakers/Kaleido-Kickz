<script>
  import { onMount, createEventDispatcher } from 'svelte';

  export let selectedColor = 'white';
  export let strokeWidth = 4; // Thicker by default
  export let eraseMode = false;

  const dispatch = createEventDispatcher();

  let canvas;
  let ctx;

  let drawing = false;
  let paths = [];
  let currentPath = null;
  let hoverPathIndex = null;

  onMount(() => {
    ctx = canvas.getContext('2d');
    resizeCanvas();
    redrawCanvas();
    window.addEventListener('resize', resizeCanvas);
  });

  function resizeCanvas() {
    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;
    redrawCanvas();
    updateGCode();
  }

  function getCanvasCoordinates(event) {
    const rect = canvas.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    };
  }

  function handleMouseDown(event) {
    const { x, y } = getCanvasCoordinates(event);

    if (eraseMode) {
      const index = getPathAtCoordinates(x, y);
      if (index !== null) {
        paths.splice(index, 1);
        hoverPathIndex = null;
        redrawCanvas();
        updateGCode();
      }
    } else {
      drawing = true;
      currentPath = {
        color: selectedColor,
        width: strokeWidth,
        points: [{ x, y }],
      };
    }
  }

  function handleMouseMove(event) {
    const { x, y } = getCanvasCoordinates(event);

    if (eraseMode) {
      const previousHoverIndex = hoverPathIndex;
      hoverPathIndex = getPathAtCoordinates(x, y);
      if (hoverPathIndex !== previousHoverIndex) {
        redrawCanvas();
      }
    } else if (drawing) {
      currentPath.points.push({ x, y });
      drawPathSegment(currentPath);
    }
  }

  function handleMouseUp() {
    if (drawing) {
      drawing = false;
      paths.push(currentPath);
      currentPath = null;
      updateGCode();
    }
  }

  function handleMouseLeave() {
    if (eraseMode) {
      hoverPathIndex = null;
      redrawCanvas();
    }
  }

  function jitter(value, amount = 1) {
    return value + (Math.random() - 0.5) * amount;
  }

  function drawPathSegment(path) {
    const points = path.points;
    const len = points.length;
    if (len < 2) return;

    ctx.save();

    ctx.strokeStyle = path.color;
    ctx.lineWidth = path.width * 2; // Thick!
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.globalAlpha = 0.85;
    ctx.shadowBlur = 1.5;
    ctx.shadowColor = path.color;

    ctx.beginPath();
    ctx.moveTo(jitter(points[len - 2].x), jitter(points[len - 2].y));
    ctx.lineTo(jitter(points[len - 1].x), jitter(points[len - 1].y));
    ctx.stroke();

    ctx.restore();
  }

  function redrawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < paths.length; i++) {
      const path = paths[i];
      const isHovered = i === hoverPathIndex && eraseMode;
      drawFullPath(path, isHovered);
    }
  }

  function drawFullPath(path, isHovered) {
    const points = path.points;
    if (points.length < 2) return;

    ctx.save();

    ctx.strokeStyle = eraseMode ? '#1c1c1c' : path.color;
    ctx.lineWidth = path.width * 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.globalAlpha = 0.85;
    ctx.shadowBlur = isHovered ? 4 : 1.5;
    ctx.shadowColor = path.color;

    ctx.beginPath();
    ctx.moveTo(jitter(points[0].x), jitter(points[0].y));
    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(jitter(points[i].x), jitter(points[i].y));
    }
    ctx.stroke();

    ctx.restore();
  }

  export function undo() {
    if (paths.length > 0) {
      paths.pop();
      redrawCanvas();
      updateGCode();
    }
  }

  function updateGCode() {
    let gcodeLines = [];

    gcodeLines.push('G21 ; Set units to millimeters');
    gcodeLines.push('G90 ; Use absolute positioning');
    gcodeLines.push('G28 ; Home all axes');

    const xMax = 100;
    const yMax = 60;

    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;

    for (const path of paths) {
      for (const point of path.points) {
        minX = Math.min(minX, point.x);
        maxX = Math.max(maxX, point.x);
        minY = Math.min(minY, point.y);
        maxY = Math.max(maxY, point.y);
      }
    }

    const xScale = maxX > minX ? xMax / (maxX - minX) : 1;
    const yScale = maxY > minY ? yMax / (maxY - minY) : 1;

    for (const path of paths) {
      if (path.points.length < 1) continue;

      const start = path.points[0];
      const startX = ((start.x - minX) * xScale).toFixed(2);
      const startY = ((start.y - minY) * yScale).toFixed(2);

      gcodeLines.push(`G0 X${startX} Y${startY} ; Rapid move to start`);
      gcodeLines.push('G1 Z-1.00 F100 ; Move down to cutting depth');

      for (const point of path.points.slice(1)) {
        const scaledX = ((point.x - minX) * xScale).toFixed(2);
        const scaledY = ((point.y - minY) * yScale).toFixed(2);
        gcodeLines.push(`G1 X${scaledX} Y${scaledY} F300 ; Cutting move`);
      }

      gcodeLines.push('G1 Z5.00 F100 ; Retract');
    }

    gcodeLines.push('M30 ; End of program');

    const gcode = gcodeLines.join('\n');
    dispatch('gcodeUpdated', { gcode });
  }

  function getPathAtCoordinates(x, y) {
    const threshold = 10;
    for (let i = paths.length - 1; i >= 0; i--) {
      const path = paths[i];
      const points = path.points;
      for (let j = 0; j < points.length - 1; j++) {
        const pointA = points[j];
        const pointB = points[j + 1];
        if (isPointNearLineSegment({ x, y }, pointA, pointB, threshold)) {
          return i;
        }
      }
    }
    return null;
  }

  function isPointNearLineSegment(point, lineStart, lineEnd, threshold) {
    const distance = distanceToSegment(point, lineStart, lineEnd);
    return distance <= threshold;
  }

  function distanceToSegment(p, v, w) {
    const l2 = (v.x - w.x) ** 2 + (v.y - w.y) ** 2;
    if (l2 === 0) return Math.hypot(p.x - v.x, p.y - v.y);
    let t = ((p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - v.y)) / l2;
    t = Math.max(0, Math.min(1, t));
    const projectionX = v.x + t * (w.x - v.x);
    const projectionY = v.y + t * (w.y - v.y);
    return Math.hypot(p.x - projectionX, p.y - projectionY);
  }
</script>

<style>
  .drawing-area {
    border: 1px solid #333;
    touch-action: none;
    background-image: url('/chalkboard.png');
    background-size: cover;
    background-position: center;
    width: 800px;
    height: 500px;
    border-radius: 12px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
  }

  canvas {
    display: block;
    width: 100%;
    height: 100%;
  }

  .erase-mode {
    cursor: crosshair;
  }

  .drawing-mode {
    cursor: crosshair;
  }
</style>

<canvas
  bind:this={canvas}
  class="drawing-area {eraseMode ? 'erase-mode' : 'drawing-mode'}"
  on:mousedown|preventDefault={handleMouseDown}
  on:mousemove|preventDefault={handleMouseMove}
  on:mouseup|preventDefault={handleMouseUp}
  on:mouseleave|preventDefault={handleMouseLeave}
/>