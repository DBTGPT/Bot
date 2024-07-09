import os
from openai import AzureOpenAI
from flask import Flask, request, jsonify, render_template
import dotenv
from azure.storage.blob import BlobServiceClient
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig
import azure.cognitiveservices.speech as speechsdk
import logging

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

def transcribe_audio(file_path):
    # Function to transcribe audio using Azure OpenAI Whisper
    pass

def synthesize_speech(text):
    # Function to synthesize speech using Azure Cognitive Services
    pass

@app.route('/api/get-response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_message = data.get('message')
    generate_audio = data.get('generateAudio', False)  # Get the generateAudio flag
    print(f"User Message: {user_message}")  # Log the user message

    try:
        response = client.chat.completions.create(
            model="DBTGPT",  # Use your deployment name here
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
                {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
                {"role": "user", "content": "Do other Azure AI services support this too?"}
            ]
        )
        
        bot_response = response.choices[0].message.content.strip()
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
