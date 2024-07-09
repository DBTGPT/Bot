import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Load your Azure OpenAI Whisper configuration from environment variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")

# Load Azure Speech key and region
speech_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_SERVICE_REGION")

# Log the loaded configurations
logging.debug(f"Azure OpenAI Endpoint: {AZURE_OPENAI_ENDPOINT}")
logging.debug(f"Azure API Key: {AZURE_API_KEY}")
logging.debug(f"Azure Speech Key: {speech_key}")
logging.debug(f"Azure Service Region: {service_region}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']

    # Save the file temporarily
    temp_file_path = os.path.join("/tmp", audio_file.filename)
    audio_file.save(temp_file_path)

    # Process the file using Azure OpenAI Whisper
    transcription = transcribe_audio(temp_file_path)

    # Clean up the temporary file
    os.remove(temp_file_path)

    if transcription:
        return jsonify({"transcription": transcription}), 200
    else:
        return jsonify({"error": "Transcription failed"}), 500

def transcribe_audio(file_path):
    headers = {
        "api-key": AZURE_API_KEY,
        "Content-Type": "application/json"
    }

    files = {
        "file": open(file_path, "rb")
    }

    response = requests.post(AZURE_OPENAI_ENDPOINT, headers=headers, files=files)

    if response.status_code == 200:
        return response.json().get("text")
    else:
        logging.error(f"Error: {response.status_code} - {response.text}")
        return None

@app.route('/api/synthesize-speech', methods=['POST'])
def synthesize_speech():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
    
        # Log the voice being used
        logging.debug(f"Using voice: {speech_config.speech_synthesis_voice_name}")

        # Define SSML with the hopeful style
        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
            <voice name='en-US-JennyNeural'>
                <prosody style='hopeful'>{text}</prosody>
            </voice>
        </speak>
        """

        audio_config = speechsdk.audio.AudioOutputConfig(filename="static/tts_output.mp3")

        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logging.debug("Speech synthesized successfully.")
            return jsonify({"audio_path": "static/tts_output.mp3"}), 200
        else:
            logging.error(f"Error synthesizing audio: {result.reason}")
            return jsonify({"error": f"Error synthesizing audio: {result.reason}"}), 500
    except Exception as e:
        logging.error(f"Exception in synthesize_speech: {e}")
        return jsonify({"error": f"Exception in synthesize_speech: {e}"}), 500

@app.route('/api/get-response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_message = data.get('message')
    generate_audio = data.get('generateAudio', False)  # Get the generateAudio flag
    print(f"User Message: {user_message}")  # Log the user message
    try:
        headers = {
            'Content-Type': 'application/json',
            'api-key': AZURE_API_KEY  # Use 'api-key' instead of 'Authorization'
        }
        json_data = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 100
        }
        # Correct the endpoint path
        response = requests.post(f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/DBTGPT/chat/completions?api-version=2023-03-15-preview", headers=headers, json=json_data)
        response_data = response.json()
        
        logging.debug(f"API Response: {response_data}")
        
        bot_response = response_data['choices'][0]['message']['content'].strip()
        
        response_data = {'response': bot_response}
        
        if generate_audio:  # Conditionally generate the audio file
            audio_path = synthesize_speech(bot_response)
            response_data['audio_path'] = audio_path

        return jsonify(response_data)
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return jsonify({'error': 'Error generating response'}), 500

if __name__ == '__main__':
    app.run(debug=True)
