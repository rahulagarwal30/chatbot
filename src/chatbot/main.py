import sys
import os
from pathlib import Path
import logging
from datetime import datetime
sys.path.append(str(Path(__file__).parent.parent.parent))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from src.chatbot.services.elasticsearch_service import perform_vector_search
from src.chatbot.services.openai_service import get_answer_from_openai
from src.chatbot.services.pusher_service import send_message

# Set up logging - moved to project root
project_root = Path(__file__).parent.parent.parent
log_directory = os.path.join(project_root, 'logs')
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = os.path.join(log_directory, 'chatbot_queries.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

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
        # Log the incoming query
        logging.info(f"Received query: {query}")
        
        # Get search results
        search_results = perform_vector_search(query)
        
        # Combine content from top results
        combined_content = ""
        for i, hit in enumerate(search_results, 1):
            content = hit['_source'].get('content', 'No content available')
            combined_content += f"\n\nDocument {i}: {content}"
        
        # Get answer from OpenAI
        answer = get_answer_from_openai(query, combined_content)
        
        # Log the answer
        logging.info(f"Answer for query '{query}': {answer}")
        
        # Send answer through Pusher
        send_message(answer)
        
        return jsonify({'message': 'Search request processed successfully'})
    except Exception as e:
        # Log the error
        logging.error(f"Error processing query '{query}': {str(e)}")
        import traceback
        error_traceback = traceback.format_exc()
        logging.error(error_traceback)
        
        return jsonify({
            'error': str(e),
            'error_type': type(e).__name__,
            'details': error_traceback
        }), 500

def run_server():
    app.run(host='0.0.0.0', port=5001)

if __name__ == '__main__':
    run_server() 