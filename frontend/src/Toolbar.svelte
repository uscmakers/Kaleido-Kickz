<script>
	export let eraseMode = false;
	export let drawingAreaRef;
	export let gcode = '';

	function handleUndo() {
		if (drawingAreaRef?.undo) {
			drawingAreaRef.undo();
		}
	}

	function handleErase() {
		const event = new CustomEvent('erase');
		dispatchEvent(event);
	}

	function handleSendToFlask() {
		const formData = new FormData();
		const blob = new Blob([gcode], { type: 'text/plain' });
		formData.append('file', blob, 'drawing.txt');

		fetch('http://192.168.2.2:5000/upload', {
			method: 'POST',
			body: formData
		})
			.then((response) => {
				if (!response.ok) throw new Error('Failed to send G-code to Flask app');
				return response.json();
			})
			.then((data) => {
				alert('✅ G-code uploaded to Raspberry Pi');
				console.log('Sent:', data);
			})
			.catch((error) => {
				alert('❌ Upload failed — check network or Flask server');
				console.error(error);
			});
	}

	function handleDownload() {
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

	function handleUpload() {
		const file = new File([new Blob([gcode], { type: 'text/plain' })], 'drawing.txt');
		const formData = new FormData();
		formData.append('file', file);

		fetch('/upload', {
			method: 'POST',
			body: formData
		})
			.then((response) => response.json())
			.then((result) => {
				alert(result.message || 'Upload complete');
				console.log('Uploaded:', result);
			})
			.catch((error) => {
				alert('Upload failed');
				console.error('Error:', error);
			});
	}
</script>

<style>
	.toolbar {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.75rem;
	}

	button {
		background-color: #f4a261;
		color: #2c2c2c;
		font-weight: 600;
		font-family: 'Fredoka', sans-serif;
		border: none;
		padding: 0.6rem 1.2rem;
		border-radius: 12px;
		cursor: pointer;
		transition: all 0.15s ease-in-out;
		box-shadow: 2px 2px 0px #00000033;
	}

	button:hover {
		background-color: #f3a14f;
		transform: scale(1.05);
	}

	button:active {
		transform: scale(0.98);
	}

	.erase-active {
		background-color: #90caf9;
		color: #1e1e1e;
	}
</style>

<div class="toolbar">
	<button on:click={handleUndo}>Undo</button>
	<button on:click={handleErase} class:erase-active={eraseMode}>
		{eraseMode ? 'Erasing' : 'Erase'}
	</button>
	<button on:click={handleSendToFlask}>Send</button>
	<button on:click={handleUpload}>Upload</button>
	<button on:click={handleDownload}>Download</button>
</div>