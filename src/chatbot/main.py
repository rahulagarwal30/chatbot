import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from src.chatbot.services.elasticsearch_service import perform_vector_search
from src.chatbot.services.openai_service import get_answer_from_openai
from src.chatbot.services.pusher_service import send_message

# Get absolute path to static folder
static_folder = os.path.join(os.path.dirname(__file__), 'static')
app = Flask(__name__, static_folder=static_folder)
CORS(app)

@app.route('/')
def index():
    return send_from_directory(static_folder, 'index.html')

@app.route('/query', methods=['POST'])
def search():
    data = request.json
    query = data.get('message')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        # Get search results
        search_results = perform_vector_search(query)
        
        # Combine content from top results
        combined_content = ""
        for i, hit in enumerate(search_results, 1):
            content = hit['_source'].get('content', 'No content available')
            combined_content += f"\n\nDocument {i}: {content}"
        
        # Get answer from OpenAI
        answer = get_answer_from_openai(query, combined_content)
        
        # Send answer through Pusher
        send_message(answer)
        
        return jsonify({'message': 'Search request processed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_server():
    app.run(port=5000)

if __name__ == '__main__':
    run_server() 