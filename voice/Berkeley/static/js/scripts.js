document.getElementById("send-btn").addEventListener("click", function() {
    sendMessage();
});

document.getElementById("mic-btn").addEventListener("click", function() {
    toggleMic();
});

document.getElementById("user-input").addEventListener("input", function() {
    toggleSendButton();
});

let messageQueue = [];
let isProcessing = false;

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
        setTimeout(processQueue, 500);  // Adjust the delay as needed
    } else {
        isProcessing = false;
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
