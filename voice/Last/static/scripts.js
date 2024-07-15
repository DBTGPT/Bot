let isListening = false;

async function toggleVoiceChat() {
    const micButton = document.getElementById('mic-button');
    const micIcon = document.getElementById('mic-icon');

    if (isListening) {
        // Stop listening
        micButton.classList.remove('blinking');
        micIcon.textContent = '🎤';
        isListening = false;
        // Stop the voice chat
        await fetch('/listen', { 
            method: 'POST', 
            body: JSON.stringify({ stop: true }), 
            headers: { 'Content-Type': 'application/json' } 
        });
    } else {
        // Start listening
        micButton.classList.add('blinking');
        micIcon.textContent = '🔴';
        isListening = true;
        // Start the voice chat
        const response = await fetch('/listen', { 
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' } 
        });
        const data = await response.json();
        if (data.status === 'error') {
            alert(data.message);
        }
        toggleVoiceChat();
    }
}
