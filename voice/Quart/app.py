import os
import uuid
import json
from quart import Quart, request, render_template, Response, jsonify, make_response
import azure.cognitiveservices.speech as speechsdk
import httpx
import asyncio
import time
from openai import AzureOpenAI
from dotenv import load_dotenv


load_dotenv()

app = Quart(__name__, static_folder='static')
request_queue = asyncio.Queue()

# setup AzureOpenAI client
gpt_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01"
)

@app.route('/config')
async def config():
    return jsonify({
        'azure_speech_key': os.getenv('AZURE_SPEECH_KEY'),
        'azure_speech_region': os.getenv('AZURE_SPEECH_REGION')
    })

# setup speech synthesizer
speech_config = speechsdk.SpeechConfig(
    endpoint=f"wss://{os.getenv('AZURE_TTS_REGION')}.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
    subscription=os.getenv("AZURE_TTS_API_KEY")
)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"

properties = {
    "SpeechSynthesis_FrameTimeoutInterval": "100000000",
    "SpeechSynthesis_RtfTimeoutThreshold": "10"
}
speech_config.set_properties_by_name(properties)

active_sessions = {}

async def handle_request(user_input, session_id):
    response = await api_call(user_input)
    return response

async def api_call(user_input):
    print(f"Simulating API call for input: {user_input}")
    await asyncio.sleep(.5)  # simulate network delay
    return f"Response to '{user_input}'"

async def generate_response(user_input, tts_queue):
    tts_request = speechsdk.SpeechSynthesisRequest(input_type=speechsdk.SpeechSynthesisRequestInputType.TextStream)
    tts_task = speech_synthesizer.speak_async(tts_request)
    
    completion = gpt_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_input}],
        stream=True
    )
    
    for chunk in completion:
        if chunk.choices[0].delta:
            tts_queue.put(chunk.choices[0].delta.content)

@app.route('/')
async def index():
    response = await render_template('index.html')
    response = await make_response(response)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/start-response', methods=['POST'])
async def start_response():
    data = await request.json
    user_input = data['input']
    use_tts = data.get('use_tts', False)
    session_id = str(uuid.uuid4())
    print(f"Received start response request: {user_input}, session: {session_id}")
    await request_queue.put((user_input, session_id))
    return jsonify({'session_id': session_id})

@app.route('/api/get-response/<session_id>', methods=['GET'])
async def get_response(session_id):
    user_input = "placeholder input based on session ID"
    print(f"Handling get-response for session_id: {session_id} with user_input: {user_input}")

    async def stream_openai_response():
        url = f"{os.getenv('AZURE_OPENAI_API_ENDPOINT')}/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-01"
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
                        print(f"Received line: {line}")  # Log the received line for debugging
                        try:
                            json_line = json.loads(line)
                            content = json_line['choices'][0]['delta'].get('content', '')
                            if content:
                                yield f"data: {content}\n\n"
                        except json.JSONDecodeError:
                            print("Failed to decode JSON")  # Log JSON decode errors
                            continue
                        await asyncio.sleep(0.1)
        yield "data: [GPT END]\n\n"

    return Response(stream_openai_response(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run()
