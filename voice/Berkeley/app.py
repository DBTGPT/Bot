import os
import uuid
import asyncio
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speechsdk
from quart import Quart, request, render_template, jsonify, Response
from dotenv import load_dotenv
import aiohttp
import time

load_dotenv()

app = Quart(__name__)

# Setup AzureOpenAI client
gpt_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01"
)

# Setup speech synthesizer with pre-connect and reuse
speech_config = speechsdk.SpeechConfig(subscription=os.getenv("AZURE_TTS_API_KEY"), region=os.getenv("AZURE_TTS_REGION"))
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
connection = speechsdk.Connection.from_speech_synthesizer(speech_synthesizer)
connection.open(True)

# Set voice and timeout properties
speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"

# Prewarm the synthesizer
speech_synthesizer.speak_text_async("Hello.").get()

# Active sessions dictionary
active_sessions = {}

async def send_request(payload):
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.example.com/endpoint", json=payload) as response:
            return await response.json()

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/api/start-response', methods=['POST'])
async def start_response():
    data = await request.json
    user_input = data['input']
    use_tts = data['use_tts']
    
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {'user_input': user_input, 'use_tts': use_tts, 'response_text': ''}
    
    return jsonify({"session_id": session_id})

@app.route('/api/get-response/<session_id>', methods=['GET'])
async def get_response(session_id):
    return Response(generate(session_id), mimetype='text/event-stream')

async def stream_openai_responses(completion):
    async for message in completion:
        if message.get("choices"):
            chunk_text = message["choices"][0]["delta"]["content"]
            yield chunk_text

async def generate(session_id):
    try:
        session = active_sessions[session_id]
        user_input = session['user_input']
        use_tts = session['use_tts']
        print(f"User input: {user_input}")

        start_time = time.time()
        completion = gpt_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ],
            stream=True
        )

        response_chunks = []
        async for chunk_text in stream_openai_responses(completion):
            print(f"Chunk text: {chunk_text}")
            session['response_text'] += chunk_text
            response_chunks.append(chunk_text)
            yield f"data: {chunk_text}\n\n"
        end_time = time.time()
        print(f"[GPT END] GPT response time: {end_time - start_time} seconds")

        # Synthesize speech concurrently
        if use_tts:
            await asyncio.gather(
                *(asyncio.to_thread(speech_synthesizer.speak_text_async(chunk).get) for chunk in response_chunks)
            )
            print("[TTS END]")

        yield "data: [GPT END]\n\n"
    except Exception as e:
        print(f"Error: {e}")
        yield f"data: Error: {str(e)}\n\n"
    finally:
        del active_sessions[session_id]

async def main():
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    asyncio.run(main())
