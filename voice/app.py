from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path
import azure.cognitiveservices.speech as speechsdk
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
speech_key = os.getenv('AZURE_SPEECH_KEY')
service_region = os.getenv('AZURE_SERVICE_REGION')

# Set OpenAI API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Log the Azure Speech Service configuration
logging.basicConfig(level=logging.DEBUG)
logging.debug(f"Azure Speech Key: {speech_key}")
logging.debug(f"Azure Service Region: {service_region}")

def synthesize_speech(text):
    try:
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
        audio_config = speechsdk.audio.AudioOutputConfig(filename="static/tts_output.mp3")

        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logging.debug("Speech synthesized successfully.")
            return "static/tts_output.mp3"
        else:
            logging.error(f"Error synthesizing audio: {result.reason}")
            return None
    except Exception as e:
        logging.error(f"Exception in synthesize_speech: {e}")
        return None

def complete_sentence(client, text, max_tokens=50):
    if text[-1] not in ['.', '!', '?']:  # If the text does not end with a sentence-ending punctuation
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": text}],
            max_tokens=max_tokens
        )
        # Ensure we append only up to the next sentence end
        additional_text = response.choices[0].message['content']
        first_sentence_end = additional_text.find('.') + 1
        if first_sentence_end == 0:
            first_sentence_end = len(additional_text)
        text += additional_text[:first_sentence_end]
    return text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/get-response', methods=['POST'])
def get_response():
    user_message = request.json.get('message')
    print(f"User Message: {user_message}")  # Log the user message
    try:
        # Generate a completion using the GPT-4o model
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=100
        )
        logging.debug(f"API Response: {response}")
        
        bot_response = response.choices[0].message.content.strip()
        bot_response = complete_sentence(client, bot_response, max_tokens=50)  # Complete the sentence if cut off
        audio_path = synthesize_speech(bot_response)

        return jsonify({'response': bot_response, 'audio_path': audio_path})
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return jsonify({'error': 'Error generating response'}), 500



if __name__ == '__main__':
    app.run(debug=True)