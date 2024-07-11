document.getElementById("send-btn").addEventListener("click", function() {
    const userInput = document.getElementById("user-input").value;
    sendMessage(userInput);
});

document.getElementById("mic-btn").addEventListener("click", function() {
    toggleMic();
});

document.getElementById("user-input").addEventListener("input", function() {
    toggleSendButton();
});

let messageQueue = [];
let isProcessing = false;
let isMicOn = false;
let recognition;

function sendMessage(userInput) {
    if (userInput.trim() !== "") {
        addMessageToChat("You", userInput);
        document.getElementById("user-input").value = "";

        fetch("/api/start-response", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ input: userInput, use_tts: isMicOn })
        })
        .then(response => response.json())
        .then(data => {
            if (data.session_id) {
                const sessionId = data.session_id;
                const eventSource = new EventSource(`/api/get-response/${sessionId}`);
                eventSource.onmessage = function(event) {
                    if (event.data !== "[GPT END]") {
                        messageQueue.push(event.data);
                        if (!isProcessing) {
                            processQueue();
                        }
                    } else {
                        eventSource.close();
                    }
                };
                eventSource.onerror = function(err) {
                    console.error("EventSource failed:", err);
                    addMessageToChat("Bot", "Sorry, something went wrong.");
                    eventSource.close();
                };
            } else {
                addMessageToChat("Bot", "Sorry, something went wrong.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            addMessageToChat("Bot", "Sorry, something went wrong.");
        });
    }
}

function processQueue() {
    if (messageQueue.length > 0) {
        isProcessing = true;
        const chunk = messageQueue.shift();
        addMessageToChat("Bot", chunk, true);
        setTimeout(processQueue, 100);  // Reduced the delay for faster processing
    } else {
        isProcessing = false;
    }
}

function toggleMic() {
    isMicOn = !isMicOn;
    const micBtn = document.getElementById("mic-btn");
    if (isMicOn) {
        micBtn.classList.add("active");
        micBtn.innerHTML = "🎤 (On)";
        startRecognition();
    } else {
        micBtn.classList.remove("active");
        micBtn.innerHTML = "🎤 (Off)";
        stopRecognition();
    }
    console.log("Microphone toggled", isMicOn);
}

function startRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        console.log('Speech recognition not supported');
        return;
    }
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = function() {
        console.log('Speech recognition started');
    };

    recognition.onresult = function(event) {
        if (event.results.length > 0) {
            const userInput = event.results[0][0].transcript;
            console.log('Speech recognized:', userInput);
            sendMessage(userInput);  // Immediate processing of recognized speech
        }
    };

    recognition.onerror = function(event) {
        console.log('Speech recognition error:', event.error);
    };

    recognition.onend = function() {
        console.log('Speech recognition ended');
        if (isMicOn) {
            recognition.start();  // Restart recognition if mic is still on
        }
    };

    recognition.start();
}

function stopRecognition() {
    if (recognition) {
        recognition.stop();
    }
}

function addMessageToChat(sender, message, append = false) {
    const chatOutput = document.getElementById("chat-output");
    if (append) {
        const lastMessage = chatOutput.lastElementChild;
        if (lastMessage && lastMessage.classList.contains(`${sender.toLowerCase()}-message`)) {
            lastMessage.innerHTML += message;
            chatOutput.scrollTop = chatOutput.scrollHeight;
            return;
        }
    }
    const messageElement = document.createElement("div");
    messageElement.classList.add(`${sender.toLowerCase()}-message`, 'message');
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatOutput.appendChild(messageElement);
    chatOutput.scrollTop = chatOutput.scrollHeight;
}

function toggleSendButton() {
    const userInput = document.getElementById("user-input").value;
    const sendButton = document.getElementById("send-btn");
    sendButton.disabled = userInput.trim() === "";
}

// Initialize send button state
toggleSendButton();
