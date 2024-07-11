import os
import uuid
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speechsdk
from flask import Flask, request, render_template, Response, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Setup AzureOpenAI client
gpt_client = AzureOpenAI(azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT"), api_key=os.getenv("AZURE_OPENAI_API_KEY"), api_version="2024-02-01")

# Setup speech synthesizer
speech_config = speechsdk.SpeechConfig(endpoint=f"wss://{os.getenv('AZURE_TTS_REGION')}.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
                                       subscription=os.getenv("AZURE_TTS_API_KEY"))
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

speech_synthesizer.synthesizing.connect(lambda evt: print("[audio]", end=""))

# Set a voice name
speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"

# Set timeout values to avoid SDK cancelling the request when GPT latency is too high
properties = {
    "SpeechSynthesis_FrameTimeoutInterval": "100000000",
    "SpeechSynthesis_RtfTimeoutThreshold": "10"
}
speech_config.set_properties_by_name(properties)

active_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start-response', methods=['POST'])
def start_response():
    data = request.json
    user_input = data['input']
    use_tts = data.get('use_tts', False)
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        'user_input': user_input,
        'response_text': '',
        'use_tts': use_tts
    }
    return jsonify({"session_id": session_id}), 200

@app.route('/api/get-response/<session_id>', methods=['GET'])
def get_response(session_id):
    if session_id not in active_sessions:
        return jsonify({"error": "Invalid session ID"}), 400

    def generate():
        try:
            session = active_sessions[session_id]
            user_input = session['user_input']
            use_tts = session['use_tts']
            print(f"User input: {user_input}")

            completion = gpt_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input}
                ],
                stream=True
            )

            for chunk in completion:
                if len(chunk.choices) > 0:
                    chunk_text = chunk.choices[0].delta.content
                    if chunk_text:
                        print(f"Chunk text: {chunk_text}")  # Logging chunk text
                        session['response_text'] += chunk_text
                        yield f"data: {chunk_text}\n\n"  # Stream the chunk to the client
                        if use_tts:
                            speech_synthesizer.speak_text_async(chunk_text)
            print("[GPT END]")  # Logging end of GPT response
            yield "data: [GPT END]\n\n"
        except Exception as e:
            print(f"Error: {e}")
            yield f"data: Error: {str(e)}\n\n"
        finally:
            del active_sessions[session_id]

    return Response(generate(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
