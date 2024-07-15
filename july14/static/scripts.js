const recordButton = document.getElementById('record-button');
const outputDiv = document.getElementById('output');
const feedbackDiv = document.getElementById('feedback');
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.continuous = false;
recognition.interimResults = false;
recognition.lang = 'en-US';

recordButton.addEventListener('click', () => {
    recordButton.setAttribute('aria-pressed', 'true');
    recognition.start();
});

recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript;
    outputDiv.innerHTML += `<div class="message user-message"><p><strong>You:</strong> ${transcript}</p></div>`;
    
    feedbackDiv.innerHTML = '<p>Processing...</p>';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: transcript })
        });

        if (response.ok) {
            const eventSource = new EventSource(`/events?text=${encodeURIComponent(transcript)}`);
            let botResponse = document.getElementById('bot-response');
            if (!botResponse) {
                outputDiv.innerHTML += `<div class="message bot-message"><p><strong>Bot:</strong> <span id="bot-response"></span></p></div>`;
                botResponse = document.getElementById('bot-response');
            } else {
                botResponse.innerHTML = ''; // Clear previous response if any
            }
            eventSource.onmessage = function(event) {
                botResponse.innerHTML += event.data;
                feedbackDiv.innerHTML = ''; // Clear the processing message
            };
            eventSource.onerror = function() {
                eventSource.close();
                feedbackDiv.innerHTML = `<p>Error receiving updates. Please try again.</p>`;
            };
        } else {
            const result = await response.json();
            feedbackDiv.innerHTML = `<p>${result.error}</p>`;
        }
    } catch (error) {
        feedbackDiv.innerHTML = `<p>Error: ${error.message}. Please try again.</p>`;
    }

    outputDiv.scrollTop = outputDiv.scrollHeight;
    recordButton.setAttribute('aria-pressed', 'false');
};

recognition.onerror = (event) => {
    feedbackDiv.innerHTML = `Error: ${event.error}. Please try again.`;
};
