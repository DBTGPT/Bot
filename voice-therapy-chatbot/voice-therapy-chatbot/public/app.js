function getBotResponse(message) {
    fetch('/api/get-response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
    })
    .then(response => response.json())
    .then(data => {
        if (data.response) {
            const botMessage = data.response;
            displayMessage("Bot", botMessage);
            speak(botMessage);
        } else {
            displayMessage("Bot", "Sorry, I couldn't understand that. Could you please repeat?");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        displayMessage("Bot", "There was an error processing your request. Please try again.");
    });
}
