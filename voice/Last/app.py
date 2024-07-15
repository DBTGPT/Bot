import os
import azure.cognitiveservices.speech as speechsdk
from openai import AzureOpenAI
from dotenv import load_dotenv
from quart import Quart, jsonify, request, render_template
import asyncio
import concurrent.futures
import logging


# Configure logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.environ.get('OPEN_AI_ENDPOINT'),
    api_key=os.environ.get('OPEN_AI_KEY'),
    api_version="2023-05-15"
)

deployment_id = os.environ.get('OPEN_AI_DEPLOYMENT_NAME')

speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

speech_config.speech_recognition_language = "en-US"
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

speech_config.speech_synthesis_voice_name = 'en-US-JennyMultilingualNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config)

tts_sentence_end = [".", "!", "?", ";", "。", "！", "？", "；", "\n"]

app = Quart(__name__, template_folder='templates', static_folder='static')

def recognize_speech_sync():
    """Synchronously recognize speech using the Azure SDK."""
    result_future = speech_recognizer.recognize_once_async()
    return result_future.get()

async def recognize_speech():
    """Run the synchronous recognition in an executor."""
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, recognize_speech_sync)
    return result

    async for chunk in response:
        if len(chunk.choices) > 0:
            chunk_message = chunk.choices[0].delta.content
            if chunk_message is not None:
                collected_messages.append(chunk_message)
                if any(chunk_message.endswith(punct) for punct in tts_sentence_end):
                    text = ''.join(collected_messages).strip()
                    if text:
                        print(f"Speech synthesized to speaker for: {text}")
                        last_tts_request = speech_synthesizer.speak_text_async(text)
                        collected_messages.clear()
    if last_tts_request:
        last_tts_request.get()  # Correctly wait for the synthesizer to complete

@app.route('/listen', methods=['POST'])
async def listen():
    try:
        speech_recognition_result = await recognize_speech()
        
        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            logging.debug(f"Recognized Speech: {speech_recognition_result.text}")
            if speech_recognition_result.text.strip().lower() == "stop":
                return jsonify({"status": "success", "message": "Conversation ended"})
            await ask_openai(speech_recognition_result.text)
            return jsonify({"status": "success", "message": "Response synthesized"})
        else:
            logging.debug(f"Recognition failed: {speech_recognition_result.reason}")
            return jsonify({"status": "error", "message": "Speech not recognized"}), 400
    except Exception as e:
        logging.error(f"Error during speech recognition: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.errorhandler(404)
async def not_found(error):
    return jsonify({"status": "error", "message": "Not Found"}), 404

@app.errorhandler(500)
async def internal_error(error):
    return jsonify({"status": "error", "message": "Internal Server Error"}), 500

@app.route('/')
async def index():
    return await render_template('index.html')

async def ask_openai(prompt):
    response = client.chat.completions.create(model=deployment_id, max_tokens=200, stream=True, messages=[
        {"role": "user", "content": prompt}
    ])
    collected_messages = []
    last_tts_request = None

@app.route('/chat', methods=['POST'])
async def chat():
    data = await request.get_json()
    prompt = data.get('prompt', '')
    if prompt:
        await ask_openai(prompt)
        return jsonify({"status": "success", "message": "Response synthesized"})
    return jsonify({"status": "error", "message": "No prompt provided"}), 400

if __name__ == '__main__':
    app.run()
