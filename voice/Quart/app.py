import os
import uuid
import json
from quart import Quart, request, render_template, Response, jsonify
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
import httpx
import asyncio
import json
import

load_dotenv()

app = Quart(__name__, static_folder='static')
request_queue = asyncio.Queue()
RATE_LIMIT_INTERVAL = 30  # seconds
last_request_time = 0

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

async def handle_request(user_input, session_id):
    global last_request_time
    current_time = time.time()
    if current_time - last_request_time < RATE_LIMIT_INTERVAL:
        await asyncio.sleep(RATE_LIMIT_INTERVAL - (current_time - last_request_time))
    # Simulate API call
    response = await api_call(user_input)
    last_request_time = time.time()
    return response

async def api_call(user_input):
    # Simulate a call to the AI API
    await asyncio.sleep(2)  # simulate network delay
    return f"Response to '{user_input}'"

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/api/start-response', methods=['POST'])
async def start_response():
    data = await request.json
    user_input = data['input']
    use_tts = data.get('use_tts', False)
    session_id = str(int(time.time()))
    await request_queue.put((user_input, session_id))
    return jsonify({'session_id': session_id})

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
    async def event_stream():
        while True:
            user_input, sid = await request_queue.get()
            if sid == session_id:
                response = await handle_request(user_input, session_id)
                for char in response:
                    yield f"data: {char}\n\n"
                    await asyncio.sleep(0.05)  # Typing effect speed
                yield "data: [GPT END]\n\n"
                break
            else:
                await request_queue.put((user_input, sid))
                await asyncio.sleep(1)
    return Response(event_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)