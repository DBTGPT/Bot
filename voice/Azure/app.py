import os
import base64
import requests
from quart import Quart, request, jsonify, render_template
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
GPT4V_KEY = os.getenv("YOUR_API_KEY")
GPT4V_ENDPOINT = "https://berkeleydbtgpt.openai.azure.com/openai/deployments/DBTGPT/chat/completions?api-version=2024-02-15-preview"

# Initialize Quart app
app = Quart(__name__)

@app.route('/')
async def home():
    return await render_template('index.html')

@app.route('/process', methods=['POST'])
async def process_message():
    data = await request.get_json()
    user_message = data.get('message')
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    payload = {
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ],
        "temperature": 0.5,
        "top_p": 0.95,
        "max_tokens": 800
    }

    headers = {
        "Content-Type": "application/json",
        "api-key": GPT4V_KEY,
    }

    try:
        response = await app.loop.run_in_executor(
            None, lambda: requests.post(GPT4V_ENDPOINT, headers=headers, json=payload)
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to make the request. Error: {e}"}), 500

    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)
