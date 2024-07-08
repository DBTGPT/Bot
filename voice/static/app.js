const speechSynthesis = window.speechSynthesis;
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
let isRecognizing = false;

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
        document.getElementById("user-input").value = '';  // Clear input field after sending
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
        if (data.response) {
            const botMessage = data.response;
            displayMessage("Bot", botMessage);
            if (data.audio_path) {
                playAudioResponse(data.audio_path);  // Play the audio file
            } else {
                speak(botMessage);  // Fallback to speak function if audio path is not available
            }
        } else {
            displayMessage("Bot", "Sorry, I couldn't understand that. Could you please repeat?");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        displayMessage("Bot", "There was an error processing your request. Please try again.");
    });
}

function playAudioResponse(audioPath) {
    const audioElement = document.getElementById("tts-audio");
    audioElement.src = audioPath;  // Ensure the path is correctly received
    audioElement.play();
}

function toggleVoiceRecognition() {
    const talkButton = document.getElementById("talk-button");
    if (isRecognizing) {
        recognition.stop();
        isRecognizing = false;
        talkButton.textContent = "Talk";
    } else {
        recognition.start();
        isRecognizing = true;
        talkButton.textContent = "Pause";
    }
}

recognition.onresult = (event) => {
    const voiceInput = event.results[0][0].transcript;
    displayMessage("User", voiceInput);
    getBotResponse(voiceInput);
};

recognition.onend = () => {
    if (isRecognizing) {
        recognition.start();
    }
};
