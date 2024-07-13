document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("input-form");
    const inputField = document.getElementById("user-input");
    const responseContainer = document.getElementById("response-container");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const userInput = inputField.value;
        const useTts = document.getElementById("use-tts").checked;
        responseContainer.innerHTML = '';  // Clear previous response

        try {
            // Start response session
            const startResponse = await fetch("/api/start-response", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ input: userInput, use_tts: useTts })
            });

            const startData = await startResponse.json();
            const sessionId = startData.session_id;

            // Create a single paragraph element for the response
            const paragraph = document.createElement("p");
            responseContainer.appendChild(paragraph);

            // Get response stream
            const eventSource = new EventSource(`/api/get-response/${sessionId}`);
            
            eventSource.onmessage = (event) => {
                const data = event.data;

                if (data === "[GPT END]") {
                    eventSource.close();
                } else {
                    // Append text to the same paragraph for natural flow
                    paragraph.textContent += data;
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
