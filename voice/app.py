import os
from flask import Flask, Response, request, render_template
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get-response', methods=['POST'])
def get_response():
    user_input = request.json['input']
    response = client.chat.completions.create(
        model="DBTGPT",  # Ensure this is the correct deployment name
        messages=[{"role": "user", "content": user_input}],
        stream=True
    )

    def generate():
        for chunk in response:
            if 'choices' in chunk:
                yield f"data: {chunk['choices'][0]['delta']['content']}\n\n"

    return Response(generate(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
