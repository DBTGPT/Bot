document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-input");
    const inputField = document.getElementById("user-input");
    const responseContainer = document.getElementById("chat-window");
    const micButton = document.getElementById("mic-btn");
    let recognition;

    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            micButton.classList.add('active');
            micButton.setAttribute('aria-pressed', 'true');
        };

        recognition.onend = () => {
            micButton.classList.remove('active');
            micButton.setAttribute('aria-pressed', 'false');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            inputField.value = transcript;
        };

        micButton.addEventListener('click', () => {
            if (recognition) {
                recognition.start();
            }
        });
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const userInput = inputField.value;
        inputField.value = ''; // Clear input field

        try {
            const startResponse = await fetch("/api/start-response", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ input: userInput })
            });

            if (!startResponse.ok) {
                throw new Error('Network response was not ok');
            }

            const startData = await startResponse.json();
            const sessionId = startData.session_id;

            const userMessageBubble = document.createElement("p");
            userMessageBubble.classList.add("message", "user-message");
            userMessageBubble.textContent = userInput;
            responseContainer.appendChild(userMessageBubble);

            const botMessageBubble = document.createElement("p");
            botMessageBubble.classList.add("message", "bot-message");
            responseContainer.appendChild(botMessageBubble);

            const eventSource = new EventSource(`/api/get-response/${sessionId}`);
            let responseText = '';

            eventSource.onmessage = (event) => {
                const data = event.data;

                if (data === "[GPT END]") {
                    eventSource.close();
                } else {
                    responseText += data;
                    botMessageBubble.textContent = responseText; // Update the bubble with the accumulated text
                }
            };

            eventSource.onerror = (error) => {
                console.error("Error: ", error);
                eventSource.close();
            };

        } catch (error) {
            console.error("Error: ", error);
        }
    });
});
