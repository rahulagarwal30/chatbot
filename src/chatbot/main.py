import sys
import os
from pathlib import Path
import logging
from datetime import datetime
import threading
from functools import partial
from user_agents import parse
import uuid
from flask import session
sys.path.append(str(Path(__file__).parent.parent.parent))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from src.chatbot.services.elasticsearch_service import perform_vector_search, es_client
from src.chatbot.services.user_service import get_location_from_ip, log_user_info
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
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return send_from_directory(static_folder, 'index.html')

@app.route('/query', methods=['POST'])
def search():
    data = request.json
    query = data.get('message')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # Get or create session ID
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
    
    # Get user agent and IP information
    user_agent_string = request.headers.get('User-Agent', 'Unknown')
    user_agent = parse(user_agent_string)
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)

    # Start processing in background thread
    thread = threading.Thread(
        target=process_query,
        args=(query, user_agent, ip_address, session_id)
    )
    thread.start()
    
    return jsonify({'message': 'Query received and being processed'}), 202

def process_query(query, user_agent, ip_address, session_id):
    try:
        # Start location lookup in background thread
        location_thread = threading.Thread(
            target=process_location_info,
            args=(query, user_agent, ip_address)
        )
        location_thread.daemon = True  # Make thread daemon so it doesn't block program exit
        location_thread.start()
        
        # Pass the logger directly
        log_user_info(query=query, user_agent=user_agent, ip_address=ip_address, logger=logging)
        
        # Continue with rest of processing
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
        send_message(answer)
        
    except Exception as e:
        # Log the error
        logging.error(f"Error processing query '{query}': {str(e)}")
        import traceback
        error_traceback = traceback.format_exc()
        logging.error(error_traceback)
        
        # Send error message through Pusher
        error_message = f"Sorry, an error occurred: {str(e)}"
        send_message(error_message)

def process_location_info(query, user_agent, ip_address):
    try:
        location = get_location_from_ip(ip_address)
        # Log the location information separately
        logging.info(f"Location for IP {ip_address}: {location}")
    except Exception as e:
        logging.error(f"Error getting location for IP {ip_address}: {str(e)}")

def run_server():
    app.run(host='0.0.0.0', port=5001)

if __name__ == '__main__':
    run_server() 