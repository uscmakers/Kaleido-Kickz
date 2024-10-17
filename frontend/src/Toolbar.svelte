<script>
    import { createEventDispatcher } from 'svelte';
  
    export let eraseMode = false;
  
    const dispatch = createEventDispatcher();
  
    function handleUndo() {
      dispatch('undo');
    }
  
    function handleErase() {
      dispatch('erase');
    }
  
    function handleDownload() {
      dispatch('downloadGCode');
    }
  </script>
  
  <style>
    .toolbar {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    button {
      padding: 8px 16px;
    }
  </style>
  
  <div class="toolbar">
    <button on:click={handleUndo} title="Undo the last action">Undo</button>
    <button on:click={handleErase} title={eraseMode ? 'Disable Erase Mode' : 'Enable Erase Mode'}>
      {eraseMode ? 'Erase Mode On' : 'Erase Mode Off'}
    </button>
    <button on:click={handleDownload} title="Download the G-code file">Download G-code</button>
  </div>
  