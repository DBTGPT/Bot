import os
import azure.cognitiveservices.speech as speechsdk
from openai import AzureOpenAI
from dotenv import load_dotenv
from quart import Quart, request, jsonify, render_template, Response
import asyncio

load_dotenv()

# Initialize Quart app
app = Quart(__name__)

# Setup Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.environ.get('OPEN_AI_ENDPOINT'),
    api_key=os.environ.get('OPEN_AI_KEY'),
    api_version="2023-05-15"
)

# Custom deployment name
deployment_id = os.environ.get('OPEN_AI_DEPLOYMENT_NAME')

# Setup Azure Speech services
speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

# Speech recognizer and synthesizer setup
speech_config.speech_recognition_language = "en-US"
speech_config.speech_synthesis_voice_name = 'en-US-AvaMultilingualNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config)

# TTS sentence end marks
tts_sentence_end = [".", "!", "?", ";", "。", "！", "？", "；", "\n"]

# Function to prompt Azure OpenAI and synthesize response
async def ask_openai(prompt):
    response = client.chat.completions.create(model=deployment_id, max_tokens=200, stream=True, messages=[
        {"role": "user", "content": prompt}
    ])
    last_tts_request = None  # Ensure last_tts_request is defined

    async def event_stream():
        nonlocal last_tts_request  # Ensure the variable is correctly scoped
        collected_messages = []
        for chunk in response:
            if len(chunk.choices) > 0:
                chunk_message = chunk.choices[0].delta.content
                if chunk_message:
                    collected_messages.append(chunk_message)
                    yield f"data: {chunk_message}\n\n"
                    if any(chunk_message.endswith(punct) for punct in tts_sentence_end):
                        text = ''.join(collected_messages).strip()
                        if text and not last_tts_request:
                            last_tts_request = speech_synthesizer.speak_text_async(text)
                            collected_messages.clear()
        if last_tts_request:
            last_tts_request.get()

    return event_stream

# Quart route for handling chat requests
@app.route('/chat', methods=['POST'])
async def chat():
    data = await request.get_json()
    user_text = data.get('text')
    
    # Get OpenAI response and synthesize speech
    try:
        event_stream = await ask_openai(user_text)
        return Response(event_stream(), mimetype='text/event-stream')  # Correctly handle the generator
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# New route for handling SSE
@app.route('/events', methods=['GET'])
async def events():
    user_text = request.args.get('text')
    
    # Get OpenAI response and synthesize speech
    event_stream = await ask_openai(user_text)
    return Response(event_stream(), mimetype='text/event-stream')

# Route to serve the index.html
@app.route('/')
async def index():
    return await render_template('index.html')

# Main function to run the app
if __name__ == '__main__':
    app.run()
