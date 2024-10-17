<script>
  import { onMount, createEventDispatcher } from 'svelte';

  export let selectedColor = 'black';
  export let strokeWidth = 2;
  export let eraseMode = false; // Now a regular prop

  const dispatch = createEventDispatcher();

  let canvas;
  let ctx;

  let drawing = false;
  let paths = []; // Store all drawn paths
  let currentPath = null;

  let hoverPathIndex = null; // Index of the path currently hovered over

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
    updateGCode(); // Update G-code after resizing
  }

  function getCanvasCoordinates(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    return { x, y };
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

  function drawPathSegment(path) {
    const points = path.points;
    const len = points.length;
    if (len < 2) return;

    ctx.strokeStyle = path.color;
    ctx.lineWidth = path.width;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();
    ctx.moveTo(points[len - 2].x, points[len - 2].y);
    ctx.lineTo(points[len - 1].x, points[len - 1].y);
    ctx.stroke();
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

    if (isHovered) {
      // Apply shadow or outline to highlight the path
      ctx.strokeStyle = path.color;
      ctx.lineWidth = path.width;
      ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
      ctx.shadowBlur = 10;
    } else {
      ctx.strokeStyle = path.color;
      ctx.lineWidth = path.width;
    }

    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.stroke();

    ctx.restore();
  }

  // Undo functionality
  export function undo() {
    if (paths.length > 0) {
      paths.pop();
      redrawCanvas();
      updateGCode();
    }
  }

  // Generate G-code
  function updateGCode() {
    let gcodeLines = [];

    // Initial G-code commands
    gcodeLines.push('G21 ; Set units to millimeters');
    gcodeLines.push('G90 ; Use absolute positioning');
    gcodeLines.push('G28 ; Home all axes');

    for (const path of paths) {
      if (path.points.length < 1) continue;

      const start = path.points[0];
      gcodeLines.push(`G0 X${start.x.toFixed(2)} Y${start.y.toFixed(2)} ; Rapid move to start`);

      // Begin cutting
      gcodeLines.push('G1 Z-1.00 F100 ; Move down to cutting depth');

      for (const point of path.points.slice(1)) {
        gcodeLines.push(`G1 X${point.x.toFixed(2)} Y${point.y.toFixed(2)} F300 ; Cutting move`);
      }

      // Retract
      gcodeLines.push('G1 Z5.00 F100 ; Retract');
    }

    gcodeLines.push('M30 ; End of program');

    const gcode = gcodeLines.join('\n');
    dispatch('gcodeUpdated', { gcode });
  }

  // Improved hit detection
  function getPathAtCoordinates(x, y) {
    const threshold = 10; // Adjust as needed
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
    border: 1px solid #ccc;
    touch-action: none;
    background-color: white;
    width: 800px;
    height: 500px;
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
    cursor: crosshair; /* Replace with paintbrush cursor if available */
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
