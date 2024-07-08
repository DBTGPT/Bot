const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
let isRecognizing = false;

document.addEventListener("DOMContentLoaded", () => {
    greetUser();
});

function greetUser() {
    const greeting = "Hello, how are you doing today?";
    displayMessage("Bot", greeting);
    speak(greeting);
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
    console.log("Sending message to server:", message);  // Log the message
    fetch('/api/get-response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Parsed server response:", data);  // Log the parsed server response
        if (data.response) {
            const botMessage = data.response;
            displayMessage("Bot", botMessage);  // Ensure the message is displayed first
            if (data.audio_path) {
                console.log("Playing audio response from:", data.audio_path);
                playAudioResponse(data.audio_path);  // Play the audio file
            } else {
                console.log("No audio path provided, using TTS.");
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
    // Remove any existing audio element
    const existingAudioElement = document.getElementById("tts-audio");
    if (existingAudioElement) {
        existingAudioElement.parentNode.removeChild(existingAudioElement);
    }

    // Create a new audio element
    const audioElement = document.createElement("audio");
    audioElement.id = "tts-audio";
    audioElement.src = audioPath;
    audioElement.autoplay = true;
    audioElement.onended = () => {
        console.log("Audio playback ended.");
    };

    // Append the new audio element to the body
    document.body.appendChild(audioElement);

    console.log("Audio element created and playback started.");
}

function speak(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onend = () => {
        console.log("Speech synthesis ended.");
    };
    window.speechSynthesis.speak(utterance);
}

function startVoiceRecognition() {
    if (isRecognizing) {
        recognition.stop();
        isRecognizing = false;
        document.querySelector("button[onclick='startVoiceRecognition()']").textContent = "Talk";
    } else {
        recognition.start();
        isRecognizing = true;
        document.querySelector("button[onclick='startVoiceRecognition()']").textContent = "Pause";
    }
}

recognition.onresult = (event) => {
    const voiceInput = event.results[0][0].transcript;
    console.log("Voice input recognized:", voiceInput);  // Log the recognized voice input
    displayMessage("User", voiceInput);
    getBotResponse(voiceInput);
};

recognition.onend = () => {
    console.log("Recognition ended. isRecognizing:", isRecognizing);  // Log recognition end
    if (isRecognizing) {
        recognition.start();
    }
};
