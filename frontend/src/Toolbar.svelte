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
    dispatch('uploadGCode');
    
  }

  function handleSendToFlask() {
    dispatch('sendToFlask');
    // Show a notification to the user
    alert('G-code has been sent to the Flask server successfully. Please check the server for the file.');
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
  <button on:click={handleSendToFlask} title="Send the G-code to Flask app">Send to Flask</button>
</div>
