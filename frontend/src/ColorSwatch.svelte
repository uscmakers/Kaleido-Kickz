<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
  
    export let selectedColor = 'black';
  
    const colors = [
      'black', 'red', 'green', 'blue',
      'yellow', 'orange', 'purple', 'brown',
    ];
  
    function selectColor(color) {
      selectedColor = color;
      dispatch('colorSelected', { color });
    }
  </script>
  
  <style>
    .swatch {
      display: flex;
      gap: 8px;
      padding: 8px;
    }
    .color-box {
      width: 24px;
      height: 24px;
      cursor: pointer;
      border: 2px solid transparent;
    }
    .selected {
      border: 2px solid #000;
    }
    .color-box:focus {
      outline: 2px solid blue;
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
  