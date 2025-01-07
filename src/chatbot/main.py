import sys
import os
from pathlib import Path
import logging
from datetime import datetime
import threading
import uuid
from flask import session
sys.path.append(str(Path(__file__).parent.parent.parent))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from src.chatbot.services.elasticsearch_service import perform_vector_search, es_client
from src.chatbot.services.user_service import collect_user_info
from src.chatbot.services.openai_service import get_answer_from_openai
from src.chatbot.services.pusher_service import send_message
from src.chatbot.services.session_service import session_manager


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
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    with open(os.path.join(static_folder, 'index.html'), 'r') as f:
        template = f.read()
    return template

@app.route('/query', methods=['POST'])
def search():
    data = request.json
    query = data.get('message')
    device_id = data.get('device_id')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # Collect and log user information
    user_info = collect_user_info(request, session, logger=logging)
    
    # Start query processing in background thread
    thread = threading.Thread(
        target=process_query,
        args=(query, user_info['session_id'], device_id)
    )
    thread.start()
    
    return jsonify({'message': 'Query received and being processed'}), 202

def process_query(query, session_id, device_id):
    try:
        logging.info(f"Device ID: {device_id}")
        logging.info(f"Session ID: {session_id}")

        # Process query
        search_results = perform_vector_search(query)
        
        # Combine content from top results
        combined_content = ""
        for i, hit in enumerate(search_results, 1):
            content = hit['_source'].get('content', 'No content available')
            combined_content += f"\n\nDocument {i}: {content}"
        
        # Get answer from OpenAI
        answer = get_answer_from_openai(query, combined_content, session_id)
        
        # Log the answer
        logging.info(f"Answer for query '{query}': {answer}")
        
        # Send answer through Pusher
        send_message(answer, device_id)
        
    except Exception as e:
        # Log the error
        logging.error(f"Error processing query '{query}': {str(e)}")
        import traceback
        error_traceback = traceback.format_exc()
        logging.error(error_traceback)
        
        # Send error message through Pusher
        error_message = f"Sorry, an error occurred: {str(e)}"
        send_message(error_message, device_id)

def run_server():
    app.run(host='0.0.0.0', port=5001)

@app.route('/clear_session', methods=['POST', 'GET'])
def clear_session():
    try:
        session_id = session.get('session_id')
        if session_id:
            session_manager.clear_session(session_id)
            session.clear()  # Clear Flask session data including stored location
            logging.info(f"Cleared session for {session_id}")
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logging.error(f"Error clearing session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.before_request
def clear_session_on_refresh():
    """Clear session when page is refreshed"""
    if request.endpoint == 'index':  # Only for main page loads
        session_id = session.get('session_id')
        if session_id:
            session_manager.clear_session(session_id)
            logging.info(f"Cleared session on page refresh for {session_id}")

if __name__ == '__main__':
    run_server() 