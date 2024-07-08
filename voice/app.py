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
azure_tts_key = os.getenv("AZURE_TTS_KEY")
azure_region = os.getenv("AZURE_REGION")

# Set OpenAI API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/get-response', methods=['POST'])
def get_response():
    user_message = request.json.get('message')
    print(f"User Message: {user_message}")  # Log the user message
    try:
        # Generate a completion using the GPT-4o model
        response = client.chat_completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=100
        )
    logging.debug(f"OpenAI response: {response}")
    return jsonify({'response': response.choices[0].message.content})

@app.route('/api/get-response', methods=['POST'])
def get_response():
    user_message = request.json.get('message')
    print(f"User Message: {user_message}")  # Log the user message
    try:
        # Generate a completion using the GPT-4o model
        response = client.chat_completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=100
        )
        print(f"API Response: {response}")  # Log the API response
        bot_response = response.choices[0].message['content'].strip()
        return jsonify({'response': bot_response})
    except Exception as e:
        print(f"Error generating response: {e}")
        return jsonify({'error': 'Error generating response'}), 500

def generate_tts(text):
    try:
        speech_config = speechsdk.SpeechConfig(subscription=azure_tts_key, region=azure_region)
        audio_config = speechsdk.audio.AudioOutputConfig(filename="static/tts_output.mp3")

        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logging.debug(f"TTS generated successfully: {str(Path('static/tts_output.mp3'))}")
            return str(Path("static/tts_output.mp3"))
        else:
            logging.error(f"Error synthesizing audio: {result.reason}")
            raise Exception("Error synthesizing audio")

    except Exception as e:
        logging.error(f"Exception in generate_tts: {e}")
        raise

if __name__ == '__main__':
    app.run(debug=True)