document.getElementById("send-btn").addEventListener("click", function() {
    sendMessage();
});

document.getElementById("mic-btn").addEventListener("click", function() {
    toggleMic();
});

document.getElementById("user-input").addEventListener("input", function() {
    toggleSendButton();
});

function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    if (userInput.trim() !== "") {
        addMessageToChat("You", userInput);
        document.getElementById("user-input").value = "";

        fetch("/api/start-response", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ input: userInput })
        })
        .then(response => response.json())
        .then(data => {
            if (data.session_id) {
                const sessionId = data.session_id;
                const eventSource = new EventSource(`/api/get-response/${sessionId}`);
                eventSource.onmessage = function(event) {
                    if (event.data !== "[GPT END]") {
                        addMessageToChat("Bot", event.data, true);
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

function toggleMic() {
    // Implement the voice recognition toggle logic here
    console.log("Microphone toggled");
}

function addMessageToChat(sender, message, append = false) {
    const chatOutput = document.getElementById("chat-output");
    if (append) {
        const lastMessage = chatOutput.lastElementChild;
        if (lastMessage && lastMessage.classList.contains('bot-message')) {
            lastMessage.innerHTML += message;
            chatOutput.scrollTop = chatOutput.scrollHeight;
            return;
        }
    }
    const messageElement = document.createElement("div");
    messageElement.classList.add(`${sender.toLowerCase()}-message`);
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
