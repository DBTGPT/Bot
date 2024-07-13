import os
import uuid
import openai
import azure.cognitiveservices.speech as speechsdk
from flask import Flask, request, Response, jsonify, render_template  # Import render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Setup OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Setup speech synthesizer
speech_config = speechsdk.SpeechConfig(subscription=os.getenv("AZURE_TTS_API_KEY"), region=os.getenv("AZURE_TTS_REGION"))
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"

# Active sessions storage
active_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start-response', methods=['POST'])
def start_response():
    user_input = request.json['input']
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        'user_input': user_input,
        'response_text': ''
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
            print(f"User input: {user_input}")

            response = CLIENT.Chat.CompletionS.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input}
                ],
                stream=True
            )

            for chunk in response:
                if len(chunk.choices) > 0:
                    chunk_text = chunk.choices[0].delta.get("content", "")
                    if chunk_text:
                        print(f"Chunk text: {chunk_text}")  # Logging chunk text
                        session['response_text'] += chunk_text
                        yield f"data: {chunk_text}\n\n"  # Stream the chunk to the client

                        # Synthesize the text chunk
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
