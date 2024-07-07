const speechSynthesis = window.speechSynthesis;
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

document.addEventListener("DOMContentLoaded", () => {
    greetUser();
});

function greetUser() {
    const greeting = "Hello, how are you doing today?";
    speak(greeting);
    displayMessage("Bot", greeting);
}

function speak(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    speechSynthesis.speak(utterance);
}

function displayMessage(sender, message) {
    const chatWindow = document.getElementById("chat-window");
    const messageElement = document.createElement("div");
    messageElement.textContent = `${sender}: ${message}`;
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function sendText() {
    const userInput = document.getElementById("user-input").value;
    if (userInput) {
        displayMessage("User", userInput);
        getBotResponse(userInput);
    }
}

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
        const botMessage = data.response;
        displayMessage("Bot", botMessage);
        speak(botMessage);
    })
    .catch(error => console.error('Error:', error));
}

function startVoiceRecognition() {
    recognition.start();
}

recognition.onresult = (event) => {
    const voiceInput = event.results[0][0].transcript;
    displayMessage("User", voiceInput);
    getBotResponse(voiceInput);
};

recognition.onend = () => {
    recognition.start();
};
