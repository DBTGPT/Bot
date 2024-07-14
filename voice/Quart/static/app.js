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
        const useTts = document.getElementById("use-tts").checked;
        inputField.value = ''; // Clear input field

        try {
            const startResponse = await fetch("/api/start-response", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ input: userInput, use_tts: useTts })
            });

            const startData = await startResponse.json();
            const sessionId = startData.session_id;

            const paragraph = document.createElement("p");
            paragraph.classList.add("message", "user-message");
            paragraph.textContent = userInput;
            responseContainer.appendChild(paragraph);

            const eventSource = new EventSource(`/api/get-response/${sessionId}`);
            
            eventSource.onmessage = (event) => {
                const data = event.data;

                if (data === "[GPT END]") {
                    eventSource.close();
                } else {
                    const botMessage = document.createElement("p");
                    botMessage.classList.add("message", "bot-message");
                    botMessage.textContent += data; // Append each character
                    responseContainer.appendChild(botMessage);
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
