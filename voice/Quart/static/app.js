document.addEventListener("DOMContentLoaded", async () => {
    const response = await fetch('/config');
    const config = await response.json();

    if (!config.azure_speech_key || !config.azure_speech_region) {
        console.error("Azure Speech configuration is missing.");
        return;
    }

    const form = document.getElementById("chat-input");
    const inputField = document.getElementById("user-input");
    const responseContainer = document.getElementById("chat-window");
    const micButton = document.getElementById("mic-btn");

    if (typeof SpeechSDK !== 'undefined') {
        const speechConfig = SpeechSDK.SpeechConfig.fromSubscription(config.azure_speech_key, config.azure_speech_region);
        const audioConfig = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
        const recognizer = new SpeechSDK.SpeechRecognizer(speechConfig, audioConfig);

        micButton.addEventListener('click', () => {
            micButton.classList.add('active');
            recognizer.startContinuousRecognitionAsync();

            recognizer.recognizing = (s, e) => {
                console.log(`RECOGNIZING: Text=${e.result.text}`);
            };

            recognizer.recognized = (s, e) => {
                if (e.result.reason === SpeechSDK.ResultReason.RecognizedSpeech) {
                    console.log(`RECOGNIZED: Text=${e.result.text}`);
                    inputField.value = e.result.text;
                    micButton.classList.remove('active');
                    recognizer.stopContinuousRecognitionAsync();
                } else if (e.result.reason === SpeechSDK.ResultReason.NoMatch) {
                    console.log("NOMATCH: Speech could not be recognized.");
                }
            };

            recognizer.canceled = (s, e) => {
                console.log(`CANCELED: Reason=${e.reason}`);
                recognizer.stopContinuousRecognitionAsync();
                micButton.classList.remove('active');
            };

            recognizer.sessionStopped = (s, e) => {
                console.log("\n    Session stopped event.");
                recognizer.stopContinuousRecognitionAsync();
                micButton.classList.remove('active');
            };
        });

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const userInput = inputField.value;
            inputField.value = ''; 

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
                        botMessageBubble.textContent = responseText;
                        speakText(responseText);
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

        async function speakText(text) {
            if (window.synthesizing) {
                console.warn("Already synthesizing.");
                return;
            }
            window.synthesizing = true;

            const ttsSpeechConfig = SpeechSDK.SpeechConfig.fromSubscription(config.azure_speech_key, config.azure_speech_region);
            const ttsAudioConfig = SpeechSDK.AudioConfig.fromDefaultSpeakerOutput();
            const synthesizer = new SpeechSDK.SpeechSynthesizer(ttsSpeechConfig, ttsAudioConfig);

            synthesizer.speakTextAsync(text,
                result => {
                    if (result.reason === SpeechSDK.ResultReason.SynthesizingAudioCompleted) {
                        console.log("synthesis finished.");
                    } else {
                        console.error(`Speech synthesis canceled, ${result.errorDetails}`);
                    }
                    synthesizer.close();
                    window.synthesizing = false;
                },
                error => {
                    console.error(error);
                    synthesizer.close();
                    window.synthesizing = false;
                });
        }
    } else {
        console.error("Speech SDK not loaded.");
    }
});
