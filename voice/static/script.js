function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    const chatWindow = document.getElementById('chat-window');

    if (userInput.trim() === "") return;

    // Display user message
    const userMessage = document.createElement('div');
    userMessage.className = 'message user';
    userMessage.textContent = userInput;
    chatWindow.appendChild(userMessage);
    document.getElementById('user-input').value = '';

    fetch('/api/get-response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ input: userInput })
    }).then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');

        function read() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    return;
                }
                const chunk = decoder.decode(value, { stream: true });

                // Display bot message
                const botMessage = document.createElement('div');
                botMessage.className = 'message bot';
                botMessage.textContent = chunk;
                chatWindow.appendChild(botMessage);
                chatWindow.scrollTop = chatWindow.scrollHeight;

                read();
            });
        }
        read();
    });
}
