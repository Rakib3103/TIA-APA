from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

# Initialize your OpenAI client
api_key = os.getenv('OPENAI_API_KEY')  # Get the API key from the environment
client = OpenAI(api_key=api_key)  # Use the API key to initialize OpenAI client

# Get assistant and vector store IDs from the environment
assistant_id = os.getenv('ASSISTANT_ID')
vector_store_id = os.getenv('VECTOR_STORE_ID')

# Update the assistant with the vector store ID in the tool_resources
my_updated_assistant = client.beta.assistants.update(
    assistant_id=assistant_id,
    instructions="You are an agriculture specialist. Your role as TIA APA is to provide information on climate change in Bangladesh, specifically relating to agricultural issues and solutions, based on the contents of uploaded documents. When answering queries, if the information is available in the documents, you should present it exactly as it appears in the documents, irrespective of the language in which the query was asked. If a query is related to a specific detail such as a location, individual's name, phone number, or a described problem, and the information is available in the documents, search the documents and provide the information line by line from the document as it is presented. If the requested information is not available in the documents, clearly state that it is not found in the provided materials. Your responses will be in the language of the document's content, even if the user's query is in a different language. You will reply the questions in three points, 1. If there is any indigenous knowledge, 2. What was the solution adviced and 3. What are the new strategies that is practiced that can be implemented.",
    name="TIA APA",
    tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
)

# Create a new thread
thread = client.beta.threads.create()
thread_id = thread.id

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json['question']

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_input,
    )
    
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
        # Extract the 'value' text from the response content
        response_content = None
        
        # Check if the content is of type TextContentBlock
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
