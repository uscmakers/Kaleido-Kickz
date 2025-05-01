<script>
	import DrawingArea from './DrawingArea.svelte';
	import Toolbar from './Toolbar.svelte';
	import ColorSwatch from './ColorSwatch.svelte';
	import { writable } from 'svelte/store';

	const selectedColor = 'white';
	let drawingAreaRef;

	const eraseMode = writable(false);
	let gcode = '';
	let gcodeDisplay;

	function handleUndo() {
		drawingAreaRef.undo();
	}

	function handleErase() {
		eraseMode.update(value => !value);
	}

	function handleDownloadGCode() {
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

	function handleUploadGCode() {
		const blob = new Blob([gcode], { type: 'text/plain' });
		const file = new File([blob], 'drawing.txt', { type: 'text/plain' });
		const formData = new FormData();
		formData.append('file', file);

		fetch('/upload', {
			method: 'POST',
			body: formData
		})
			.then(response => response.json())
			.then(result => {
				alert(result.message || 'Upload complete');
				console.log('Success:', result);
			})
			.catch(error => {
				alert('Upload failed');
				console.error('Error:', error);
			});
	}

	function handleSendToFlask() {
		const formData = new FormData();
		const blob = new Blob([gcode], { type: 'text/plain' });
		formData.append('file', blob, 'drawing.txt');

		fetch('http://192.168.2.2:5000/upload', {
			method: 'POST',
			body: formData,
		})
			.then(response => {
				if (!response.ok) throw new Error('Failed to send G-code to Flask app');
				return response.json();
			})
			.then(data => {
				console.log('✅ G-code successfully sent:', data);
				alert('✅ G-code uploaded to Raspberry Pi');
			})
			.catch(error => {
				console.error('❌ Upload failed:', error);
				alert('❌ Upload failed — check network or Flask server');
			});
	}

	function handleGCodeUpdated(event) {
		gcode = event.detail.gcode;
	}

	$: {
		if (gcodeDisplay) {
			setTimeout(() => {
				gcodeDisplay.scrollTop = gcodeDisplay.scrollHeight;
			}, 0);
		}
	}
</script>

<style>
	@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600&display=swap');

	:global(body) {
		margin: 0;
		background-color: #d5d2d2;
		color: white;
		font-family: 'Fredoka', sans-serif;
	}

	.app {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 2rem;
		background: d5d2d2;
		min-height: 100vh;
	}

	.controls {
	display: flex;
	justify-content: center;
	align-items: center;
	gap: 1rem;
	width: 100%;
	padding: 1rem;
	background: transparent;
	box-shadow: none;
}
	.main-content {
		display: flex;
		flex-wrap: wrap;
		gap: 2rem;
		justify-content: center;
		width: 100%;
		max-width: 1400px;
	}

	.gcode-display {
		background: #1e1e1e;
		color: #d4d4d4;
		font-family: 'Courier New', monospace;
		border-radius: 12px;
		padding: 1.25rem;
		border: 2px solid #333;
		width: 400px;
		max-height: 500px;
		overflow-y: auto;
		box-shadow: 0 0 0 3px #111;
	}

	.gcode-display h3 {
		font-size: 1rem;
		color: #f4a261;
		margin-bottom: 1rem;
		font-weight: 600;
		border-bottom: 1px solid #444;
		padding-bottom: 0.5rem;
		text-transform: uppercase;
		letter-spacing: 1px;
	}

	.gcode-display pre {
		margin: 0;
		white-space: pre-wrap;
		word-wrap: break-word;
		font-size: 0.9rem;
		line-height: 1.4;
	}
</style>

<div class="app">
	<div class="controls">
		<Toolbar
			eraseMode={$eraseMode}
			gcode={gcode}
			drawingAreaRef={drawingAreaRef}
			on:erase={handleErase}
		/>
		<!-- <ColorSwatch selectedColor="black" /> -->
	</div>

	<div class="main-content">
		<DrawingArea
			bind:this={drawingAreaRef}
			selectedColor="#e0dbd1"
			eraseMode={$eraseMode}
			on:gcodeUpdated={handleGCodeUpdated}
		/>

		<div class="gcode-display">
			<h3>Live G-code Output:</h3>
			<pre bind:this={gcodeDisplay}>{gcode}</pre>
		</div>
	</div>
</div>