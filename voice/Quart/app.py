import os
import uuid
import json
from quart import Quart, request, render_template, Response, jsonify
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
import httpx
import asyncio

load_dotenv()

app = Quart(__name__, static_folder='static')

# Setup speech synthesizer
speech_config = speechsdk.SpeechConfig(
    endpoint=f"wss://{os.getenv('AZURE_TTS_REGION')}.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
    subscription=os.getenv("AZURE_TTS_API_KEY")
)
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
async def index():
    return await render_template('index.html')

@app.route('/api/start-response', methods=['POST'])
async def start_response():
    data = await request.json
    user_input = data['input']
    use_tts = data.get('use_tts', False)
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        'user_input': user_input,
        'response_text': '',
        'use_tts': use_tts
    }
    return jsonify({"session_id": session_id}), 200

async def fetch_stream(session, user_input):
    url = os.getenv("AZURE_OPENAI_API_ENDPOINT") + "/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-01"
    headers = {
        "Content-Type": "application/json",
        "api-key": os.getenv("AZURE_OPENAI_API_KEY")
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ],
        "stream": True
    }
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            async for line in response.aiter_lines():
                if line:
                    yield line

@app.route('/api/get-response/<session_id>', methods=['GET'])
async def get_response(session_id):
    if session_id not in active_sessions:
        return jsonify({"error": "Invalid session ID"}), 400

    async def generate():
        try:
            session = active_sessions[session_id]
            user_input = session['user_input']
            use_tts = session['use_tts']
            print(f"User input: {user_input}")

            async for line in fetch_stream(session, user_input):
                chunk = line.strip()
                print(f"Raw chunk: {chunk}")  # Debugging: print the raw chunk
                if chunk == "data: [DONE]":
                    break
                if chunk.startswith("data:"):
                    chunk_json = chunk[len("data:"):].strip()
                    try:
                        chunk_data = json.loads(chunk_json)
                        if "choices" in chunk_data and len(chunk_data["choices"]) > 0:
                            chunk_text = chunk_data["choices"][0].get("delta", {}).get("content", "")
                            if chunk_text:
                                print(f"Chunk text: {chunk_text}")
                                session['response_text'] += chunk_text
                                yield f"data: {chunk_text}\n\n"
                                if use_tts:
                                    await speech_synthesizer.speak_text_async(chunk_text)
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")  # Debugging: print JSON decode errors
            print("[GPT END]")
            yield "data: [GPT END]\n\n"
        except Exception as e:
            print(f"Error: {e}")
            yield f"data: Error: {str(e)}\n\n"
        finally:
            del active_sessions[session_id]

    return Response(generate(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
