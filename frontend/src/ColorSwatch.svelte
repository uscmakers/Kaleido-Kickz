<script>
	import { createEventDispatcher } from 'svelte';
	const dispatch = createEventDispatcher();

	export let selectedColor = 'black';

	// ✅ Only one color
	const colors = ['black'];

	function selectColor(color) {
		selectedColor = color;
		dispatch('colorSelected', { color });
	}
</script>

<style>
	.swatch {
		display: flex;
		justify-content: center;
		padding: 8px;
	}

	.color-box {
		width: 28px;
		height: 28px;
		border-radius: 50%;
		cursor: pointer;
		border: 2px solid transparent;
		transition: transform 0.2s ease;
	}

	.color-box:hover {
		transform: scale(1.1);
	}

	.selected {
		border: 2px solid #f4a261;
		box-shadow: 0 0 0 2px white;
	}

	.color-box:focus {
		outline: 2px dashed #f4a261;
	}
</style>

<div class="swatch">
	{#each colors as color}
		<div
			class="color-box {selectedColor === color ? 'selected' : ''}"
			style="background-color: {color};"
			tabindex="0"
			role="button"
			aria-label="Select color {color}"
			on:click={() => selectColor(color)}
			on:keydown={(event) => {
				if (event.key === 'Enter' || event.key === ' ') {
					selectColor(color);
				}
			}}
		></div>
	{/each}
</div>