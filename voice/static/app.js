const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
let isRecognizing = false;
let currentAudioElement = null;  // Track the current audio element

document.addEventListener("DOMContentLoaded", () => {
    greetUser();
    document.getElementById("user-input").focus();
});

function greetUser() {
    const greeting = "Hello, how are you doing today?";
    displayMessage("Bot", greeting);
    speak(greeting);
}

function displayMessage(sender, message) {
    const chatWindow = document.getElementById("chat-window");
    const messageElement = document.createElement("div");
    messageElement.classList.add("message");
    messageElement.classList.add(sender.toLowerCase());
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
        body: JSON.stringify({ message, generateAudio: isRecognizing })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Parsed server response:", data);  // Log the parsed server response
        if (data.response) {
            const botMessage = data.response;
            displayMessage("Bot", botMessage);  // Ensure the message is displayed first
            if (isRecognizing) {
                if (data.audio_path) {
                    console.log("Playing audio response from:", data.audio_path);
                    playAudioResponse(data.audio_path);  // Play the audio file
                } else {
                    console.log("No audio path provided, using TTS.");
                    speak(botMessage);  // Fallback to speak function if audio path is not available
                }
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
    // Force a fresh fetch of the audio file by appending a timestamp
    const uniqueAudioPath = audioPath + "?t=" + new Date().getTime();

    // Remove any existing audio element
    if (currentAudioElement) {
        currentAudioElement.pause();
        currentAudioElement.currentTime = 0;
        currentAudioElement.parentNode.removeChild(currentAudioElement);
    }

    // Create a new audio element
    const audioElement = document.createElement("audio");
    audioElement.id = "tts-audio";
    audioElement.src = uniqueAudioPath;
    audioElement.autoplay = true;
    audioElement.onended = () => {
        console.log("Audio playback ended.");
        currentAudioElement = null;  // Clear the reference when done
    };

    // Append the new audio element to the body
    document.body.appendChild(audioElement);
    currentAudioElement = audioElement;  // Update the reference to the current audio element

    console.log("Audio element created and playback started with path:", uniqueAudioPath);
}

function speak(text) {
    const utterance = new SpeechSynthesisUtterance(text);

    // Customize neural voice parameters
    utterance.voice = speechSynthesis.getVoices().find(voice => voice.name === "Microsoft Jenny Online (Natural)"); // Replace with desired voice name
    utterance.pitch = 1.0;  // Adjust pitch (0 to 2)
    utterance.rate = 1.0;   // Adjust rate (0.1 to 10)
    utterance.volume = 1.0; // Adjust volume (0 to 1)

    utterance.onend = () => {
        console.log("Speech synthesis ended.");
    };
    window.speechSynthesis.speak(utterance);
}

function startVoiceRecognition() {
    const talkButton = document.getElementById("talk-button");
    if (isRecognizing) {
        recognition.stop();
        isRecognizing = false;
        talkButton.classList.remove("blinking");
    } else {
        // Stop any current audio playback
        if (currentAudioElement) {
            togglePause(); // Stop the audio if it's playing
        }

        // Stop any ongoing speech synthesis
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
        }

        recognition.start();
        isRecognizing = true;
        talkButton.classList.add("blinking");
    }
}

function togglePause() {
    if (currentAudioElement) {
        currentAudioElement.pause();
        currentAudioElement.currentTime = 0;
        currentAudioElement.parentNode.removeChild(currentAudioElement);
        currentAudioElement = null;
    }

    // Stop any ongoing speech synthesis
    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
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