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
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"  # Example of a neural voice
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        # Synthesize the text to speech
        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logging.debug("Speech synthesized successfully.")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logging.error(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logging.error(f"Error details: {cancellation_details.error_details}")
    except Exception as e:
        logging.error(f"Exception in synthesize_speech: {e}")

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
        print(f"API Response: {response}")  # Log the API response
        bot_response = response.choices[0].message.content.strip()
        return jsonify({'response': bot_response})
    except Exception as e:
        print(f"Error generating response: {e}")
        return jsonify({'error': 'Error generating response'}), 500



if __name__ == '__main__':
    app.run(debug=True)