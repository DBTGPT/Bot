from flask import Flask, request, jsonify, render_template
import openai
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
openai.api_key = api_key

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_text():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    logging.debug(f"OpenAI response: {response}")
    return jsonify({'response': response.choices[0].message.content})

@app.route('/api/get-response', methods=['POST'])
def get_response():
    try:
        user_message = request.json.get('message')
        logging.debug(f"User message: {user_message}")
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        bot_response = response.choices[0].message.content
        logging.debug(f"Bot response: {bot_response}")
        audio_path = generate_tts(bot_response)
        return jsonify({'bot_response': bot_response, 'audio_path': audio_path})

    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI error: {e}")
        return jsonify({'error': 'An error occurred: {}'.format(str(e))}), 500

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