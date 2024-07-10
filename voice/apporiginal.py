import os
from openai import AzureOpenAI
from flask import Flask, request, jsonify, render_template
import dotenv
from azure.storage.blob import BlobServiceClient
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig
import azure.cognitiveservices.speech as speechsdk
import logging
import time

# Load environment variables from .env file
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load your Azure OpenAI Whisper configuration from environment variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
Azure_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

# Load Azure Speech key and region
speech_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_SERVICE_REGION")
speech_endpoint = os.getenv("AZURE_SPEECH_ENDPOINT")

# Log the loaded configurations
logging.debug(f"Azure OpenAI Endpoint: {AZURE_OPENAI_ENDPOINT}")
logging.debug(f"Azure API Key: {Azure_OPENAI_API_KEY}")
logging.debug(f"Azure Speech Key: {speech_key}")
logging.debug(f"Azure Service Region: {service_region}")
logging.debug(f"Azure Speech Endpoint: {speech_endpoint}")

# Initialize the OpenAI client
client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-01",
)

app = Flask(__name__)

# Initialize conversation history
conversation_history = [{"role": "system", "content": "You are a helpful assistant."}]

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
        return jsonify({"transcription": transcription})
    else:
        return jsonify({"error": "Transcription failed"}), 500

def transcribe_audio(audio_file_path):
    # This function will transcribe the audio using Azure Cognitive Services
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
    
    # Configure the recognizer for silence detection
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    # Set up silence detection
    stop_recognition = False

    def stop_cb(evt):
        nonlocal stop_recognition
        stop_recognition = True

    recognizer.recognized.connect(lambda evt: print(f"RECOGNIZED: {evt.result.text}"))
    recognizer.session_stopped.connect(stop_cb)
    recognizer.canceled.connect(stop_cb)

    recognizer.start_continuous_recognition_async()

    while not stop_recognition:
        time.sleep(0.1)

    recognizer.stop_continuous_recognition_async()
    
    result = recognizer.recognize_once()
    return result.text if result.reason == speechsdk.ResultReason.RecognizedSpeech else None

def synthesize_speech(text):
    try:
        speech_config = SpeechConfig(subscription=speech_key, region=service_region)
        ssml_string = f"""
        <speak version='1.0' xml:lang='en-US'>
            <voice name='en-US-JennyNeural'>
                <prosody style='hopeful'>{text}</prosody>
            </voice>
        </speak>
        """

        audio_config = speechsdk.audio.AudioOutputConfig(filename="static/tts_output.mp3")

        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_ssml_async(ssml_string).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logging.debug("Speech synthesized successfully.")
            return "static/tts_output.mp3"
        else:
            logging.error(f"Error synthesizing audio: {result.reason}")
            return None
    except Exception as e:
        logging.error(f"Exception in synthesize_speech: {e}")
        return None

@app.route('/api/get-response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_message = data.get('message')
    generate_audio = data.get('generateAudio', False)  # Get the generateAudio flag
    print(f"User Message: {user_message}")  # Log the user message

    max_retries = 5
    retry_delay = 1  # Initial delay in seconds

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="DBTGPT",
                messages=[
                    {"role": "system", "content": "You are a DBT Therapist"},
                    {"role": "user", "content": "Tell me a joke."}   
                ],
                temperature=0.5,  # Adjust temperature if necessary
                max_tokens=50,  # Adjust max tokens if necessary
                stream=True  # Set to False to receive full response at once
            )

            # Log the response from Azure OpenAI
            logging.debug(f"OpenAI Response: {response}")

            bot_response = response.choices[0].message.content.strip()
            response_data = {'response': bot_response}
            
            if generate_audio:  # Conditionally generate the audio file
                audio_path = synthesize_speech(bot_response)
                response_data['audio_path'] = audio_path

            return jsonify(response_data)

        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return jsonify({'error': 'Error generating response'}), 500

    return jsonify({'error': 'Exceeded maximum retries'}), 429

if __name__ == '__main__':
    app.run(debug=True)