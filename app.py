from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
import re

app = Flask(__name__)
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Get assistant and vector store IDs
assistant_id = os.getenv('ASSISTANT_ID')
vector_store_id = os.getenv('VECTOR_STORE_ID')

# Set up assistant with vector store in the tool_resources
my_updated_assistant = client.beta.assistants.update(
    assistant_id=assistant_id,
    instructions="You are an agriculture specialist. Your role as TIA APA is to provide information on climate change in Bangladesh, specifically relating to agricultural issues and solutions, based on the contents of uploaded documents. When answering queries, if the information is available in the documents, you should present it exactly as it appears in the documents, irrespective of the language in which the query was asked. If the requested information is not available in the documents, clearly state that it is not found in the provided materials. Your responses will be in the language of the document's content. You will reply the questions in three points, 1. If there is any indigenous knowledge, 2. What was the solution adviced and 3. What are the new strategies that is practiced that can be implemented.",
    name="TIA APA",
    tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
)

# Create a new thread for the assistant
thread = client.beta.threads.create()
thread_id = thread.id

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    # Get image and question input
    image = request.files.get('image')
    user_input = request.form.get('question', '')

    if image:
        # Read and encode image without saving
        base64_image = base64.b64encode(image.read()).decode('utf-8')

        # Send image to OpenAI Vision API
        vision_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_input},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ]
        )
        
        vision_info = vision_response.choices[0].message.content
    else:
        vision_info = "No image uploaded."

    # Send text query and image information to the assistant
    message_content = f"{user_input}\n{vision_info}"
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_content,
    )

    # Get assistant's response
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    response_message = None
    messages = client.beta.threads.messages.list(thread_id=thread_id).data

    for message in messages:
        if message.role == "assistant" and message.created_at > run.created_at:
            response_message = message
            break

    if response_message:
        # Extract and clean up response content
        response_content = " ".join(block.text.value for block in response_message.content if block.text)
        response_content = re.sub(r'(\*{1,2}|["“”])', '', response_content)
        response_content= re.sub(r'【\d+:\d+†source】', '', response_content)

        return jsonify({'response': response_content})
    else:
        return jsonify({'response': "No assistant response found."})

if __name__ == '__main__':
    app.run(debug=True)
