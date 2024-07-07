from flask import Flask, request, jsonify, send_from_directory, render_template
from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path
import azure.cognitiveservices.speech as speechsdk

app = Flask(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Instantiate the OpenAI client
client = OpenAI(api_key=api_key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_text():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return jsonify({'response': response.choices[0].message['content']})

@app.route('/api/get-response', methods=['POST'])
def get_response():
    try:
        user_message = request.json.get('message')
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        bot_response = response.choices[0].message.content  # Corrected access to message content
        audio_path = generate_tts(bot_response)
        return jsonify({'bot_response': bot_response, 'audio_path': audio_path})

    except OpenAI.error.OpenAIError as e:  # Corrected error handling
        return jsonify({'error': 'An error occurred: {}'.format(str(e))}), 500

def generate_tts(text):
    speech_config = speechsdk.SpeechConfig(subscription=azure_tts_key, region=azure_region)
    audio_config = speechsdk.audio.AudioOutputConfig(filename="static/tts_output.mp3")

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return str(Path("static/tts_output.mp3"))
    else:
        raise Exception("Error synthesizing audio")

if __name__ == '__main__':
    app.run(debug=True)