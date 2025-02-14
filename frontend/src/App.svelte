<script>
	import DrawingArea from './DrawingArea.svelte';
	import ColorSwatch from './ColorSwatch.svelte';
	import Toolbar from './Toolbar.svelte';
	import { writable } from 'svelte/store';
  
	let selectedColor = 'black';
	let strokeWidth = 2;
	let drawingAreaRef;
  
	// Store for erase mode status
	const eraseMode = writable(false);
  
	// Store for live G-code
	let gcode = '';
  
	// Reference to the G-code display element
	let gcodeDisplay;
  
	function handleColorSelected(event) {
	  selectedColor = event.detail.color;
	}
  
	function handleUndo() {
	  drawingAreaRef.undo();
	}
  
	function handleErase() {
	  // Toggle erase mode status
	  eraseMode.update(value => !value);
	}
  
	function handleDownloadGCode() {
	  // The G-code is already live-updated, so we can use the current value
	  const blob = new Blob([gcode], { type: 'text/plain' });
	  const url = URL.createObjectURL(blob);
	  const link = document.createElement('a');
	  link.href = url;
	  link.download = 'drawing.txt';
	  document.body.appendChild(link);
	  link.click();
	  document.body.removeChild(link);
	  URL.revokeObjectURL(url);
	}
  
	function handleSendToFlask() {
	  // Send G-code to Flask app
	  const formData = new FormData();
	  const blob = new Blob([gcode], { type: 'text/plain' });
	  formData.append('file', blob, 'drawing.gcode');
  
	  fetch('http://localhost:5000/upload', {
		method: 'POST',
		body: formData,
	  })
		.then(response => {
		  if (!response.ok) {
			throw new Error('Failed to send G-code to Flask app');
		  }
		  return response.json();
		})
		.then(data => {
		  console.log('G-code successfully sent:', data);
		})
		.catch(error => {
		  console.error('Error:', error);
		});
	}
  
	// Receive live G-code updates from DrawingArea
	function handleGCodeUpdated(event) {
	  gcode = event.detail.gcode;
	}
  
	// Auto-scroll the G-code display to the bottom when updated
	$: {
	  if (gcodeDisplay) {
		// Use a timeout to ensure the DOM has updated before scrolling
		setTimeout(() => {
		  gcodeDisplay.scrollTop = gcodeDisplay.scrollHeight;
		}, 0);
	  }
	}
  </script>
  
  <style>
	.app {
	  display: flex;
	  flex-direction: column;
	  align-items: center;
	  padding: 16px;
	}
	.controls {
	  display: flex;
	  gap: 16px;
	  align-items: center;
	  margin: 8px 0;
	}
	.main-content {
	  display: flex;
	  gap: 16px;
	  width: 100%;
	  max-width: 1200px;
	}
	.gcode-display {
	  width: 400px;
	  max-height: 500px;
	  overflow-y: auto;
	  background-color: #f9f9f9;
	  padding: 8px;
	  border: 1px solid #ccc;
	}
	.gcode-display pre {
	  margin: 0;
	  font-family: monospace;
	  font-size: 14px;
	  white-space: pre-wrap;
	  word-wrap: break-word;
	}
	.slider-container {
	  display: flex;
	  align-items: center;
	  gap: 8px;
	}
	.slider-container label {
	  white-space: nowrap;
	}
	.slider-container input {
	  width: 150px;
	}
  </style>
  
  <div class="app">
	<ColorSwatch on:colorSelected={handleColorSelected} />
  
	<div class="controls">
	  <Toolbar
		on:undo={handleUndo}
		on:erase={handleErase}
		on:downloadGCode={handleDownloadGCode}
		on:sendToFlask={handleSendToFlask}
		eraseMode={$eraseMode}
	  />
	  <div class="slider-container" title="Adjust Line Thickness">
		<label for="strokeWidth">Line Thickness:</label>
		<input
		  type="range"
		  id="strokeWidth"
		  min="1"
		  max="10"
		  bind:value={strokeWidth}
		/>
		<span>{strokeWidth}</span>
	  </div>
	</div>
  
	<div class="main-content">
	  <DrawingArea
		bind:this={drawingAreaRef}
		{selectedColor}
		{strokeWidth}
		eraseMode={$eraseMode}
		on:gcodeUpdated={handleGCodeUpdated}
	  />
  
	  <div class="gcode-display">
		<h3>Live G-code Output:</h3>
		<pre bind:this={gcodeDisplay}>{gcode}</pre>
	  </div>
	</div>
  </div>
  