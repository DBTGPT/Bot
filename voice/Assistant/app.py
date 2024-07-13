import os
import time
import json
import requests
from openai import OpenAI  # Ensure this matches the actual import for Azure OpenAI

client = OpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-05-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

assistant = client.assistants.create(
    instructions="You are a DBT therapist assistant. Your role is to deliver DBT skills training, provide supportive feedback, and track user progress according to DBT adherence protocols. Always use therapeutic language and follow DBT guidelines strictly. Ensure that each session includes mindfulness practices, emotion regulation skills, and distress tolerance strategies.",
    model="dbtgpt", # replace with model deployment name.
    tools=[]
)

# Create a vector store called "Financial Statements"
vector_store = client.vector_stores.create(name="Financial Statements")

# Ready the files for upload to OpenAI
file_paths = ["mydirectory/myfile1.pdf", "mydirectory/myfile2.txt"]
file_streams = [open(path, "rb") for path in file_paths]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)

# Update the assistant to use the new vector store
assistant = client.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
)

# Create a thread
thread = client.threads.create()

# Add a user question to the thread
message = client.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="hi" # Replace this with your prompt
)

# Run the thread
run = client.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)

# Looping until the run completes or fails
while run.status in ['queued', 'in_progress', 'cancelling']:
    time.sleep(1)
    run = client.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

if run.status == 'completed':
    messages = client.threads.messages.list(
        thread_id=thread.id
    )
    print(messages)
elif run.status == 'requires_action':
    # the assistant requires calling some functions
    # and submit the tool outputs back to the run
    pass
else:
    print(run.status)
