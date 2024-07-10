import os
from flask import Flask, request, jsonify, send_from_directory, render_template
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
gpt_client = AzureOpenAI(azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT"), api_key=os.getenv("AZURE_OPENAI_API_KEY"), api_version="2024-02-01")

# setup speech synthesizer
speech_config = speechsdk.SpeechConfig(endpoint=f"wss://{os.getenv('AZURE_TTS_REGION')}.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
                                       subscription=os.getenv("AZURE_TTS_API_KEY"))
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"

properties = dict()
properties["SpeechSynthesis_FrameTimeoutInterval"]="100000000"
properties["SpeechSynthesis_RtfTimeoutThreshold"]="10"
speech_config.set_properties_by_name(properties)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/get-response', methods=['POST'])
def get_response():
    data = request.json
    user_message = data['message']
    generate_audio = data.get('generateAudio', False)

    # Get GPT output stream
    completion = gpt_client.chat.completions.create(
        model="DBTGPT",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ],
        stream=True
    )

    bot_response = ""
    for chunk in completion:
        if len(chunk.choices) > 0:
            chunk_text = chunk.choices[0].delta.content
            if chunk_text:
                bot_response += chunk_text

    audio_path = None
    if generate_audio:
        tts_request = speechsdk.SpeechSynthesisRequest(input_type=speechsdk.SpeechSynthesisRequestInputType.TextStream)
        tts_task = speech_synthesizer.speak_async(tts_request)
        tts_request.input_stream.write(bot_response)
        tts_request.input_stream.close()
        result = tts_task.get()

        if result.audio_data:
            audio_path = f"static/audio_response.wav"
            with open(audio_path, 'wb') as audio_file:
                audio_file.write(result.audio_data)

    return jsonify({
        'response': bot_response,
        'audio_path': audio_path
    })

if __name__ == '__main__':
    app.run(debug=True)