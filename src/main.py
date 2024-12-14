from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from services.elasticsearch_service import perform_vector_search
from services.openai_service import get_answer_from_openai
from services.pusher_service import send_message

app = Flask(__name__, static_folder='static')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

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

if __name__ == '__main__':
    app.run(port=5000)