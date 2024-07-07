from flask import Flask, request, jsonify, render_template
import openai
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')
print(f"Loaded API Key: {openai.api_key}")  # Verify API Key is loaded

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/get-response', methods=['POST'])
def get_response():
    user_message = request.json.get('message')
    print(f"User Message: {user_message}")  # Log the user message
    try:
        response = openai.Completion.create(
            model='text-davinci-003',  # Update to a supported model
            prompt=user_message,
            max_tokens=100
        )
        print(f"API Response: {response}")  # Log the API response
        bot_response = response['choices'][0]['text'].strip()
        return jsonify({'response': bot_response})
    except Exception as e:
        print(f"Error generating response: {e}")
        return jsonify({'error': 'Error generating response'}), 500

if __name__ == '__main__':
    app.run(debug=True)
