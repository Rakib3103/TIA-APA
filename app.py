from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os
import base64

app = Flask(__name__)
load_dotenv()

# Initialize your OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Get assistant and vector store IDs from the environment
assistant_id = os.getenv('ASSISTANT_ID')
vector_store_id = os.getenv('VECTOR_STORE_ID')

# Update the assistant with the vector store ID in the tool_resources
my_updated_assistant = client.beta.assistants.update(
    assistant_id=assistant_id,
    instructions="You are an agriculture specialist. Your role as TIA APA is to provide information on climate change in Bangladesh, specifically relating to agricultural issues and solutions, based on the contents of uploaded documents. When answering queries, if the information is available in the documents, you should present it exactly as it appears in the documents, irrespective of the language in which the query was asked. If a query is related to a specific detail such as a location, individual's name, phone number, or a described problem, and the information is available in the documents, search the documents and provide the information line by line from the document as it is presented. If the requested information is not available in the documents, clearly state that it is not found in the provided materials. Your responses will be in the language of the document's content, even if the user's query is in a different language. You will reply the questions in three points: 1. If there is any indigenous knowledge, 2. What was the solution advised, and 3. What are the new strategies that are practiced that can be implemented.",
    name="TIA APA",
    tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@app.route('/ask', methods=['POST'])
def ask():
    image = request.files.get('image')
    user_input = request.form.get('question', '')

    vision_info = ""
    
    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Get base64 encoded image
        base64_image = encode_image(image_path)

        # Prepare the message for the OpenAI Vision API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the appropriate model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_input,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
        )

        # Extract the vision information
        vision_info = response.choices[0].message.content

    # Combine user input with the vision analysis
    combined_input = user_input
    if vision_info:
        combined_input += f"\nVision Analysis: {vision_info}"
    
    # Create a new thread for the assistant
    thread = client.beta.threads.create()
    thread_id = thread.id

    # Send combined input to the assistant
    assistant_response = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=combined_input,
    )

    # Create and poll the assistant's response
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
        # Extract the response content
        response_content = None
        
        if hasattr(response_message, 'content') and isinstance(response_message.content, list):
            for content_block in response_message.content:
                if hasattr(content_block, 'text') and hasattr(content_block.text, 'value'):
                    response_content = content_block.text.value
                    break
        
        if response_content is None:
            response_content = "No valid response content available."
        
        return jsonify({'response': response_content})
    else:
        return jsonify({'response': "No assistant response found."})

if __name__ == '__main__':
    app.run(debug=True)
