from openai import OpenAI
from ...config.config import OPENAI_API_KEY
from .session_service import session_manager
import logging

client = OpenAI(api_key=OPENAI_API_KEY)

def truncate_content(content, max_chars=64000):
    """Truncate content to a maximum number of characters while trying to preserve complete sentences."""
    if len(content) <= max_chars:
        return content
    
    # Find the last period within the max_chars limit
    truncated = content[:max_chars]
    last_period = truncated.rfind('.')
    
    if last_period != -1:
        return truncated[:last_period + 1]
    return truncated

def get_answer_from_openai(query, content, session_id):
    try:
        truncated_content = truncate_content(content)
        
        # Initialize session if it doesn't exist
        if not session_manager.session_exists(session_id):
            session_manager.create_session(session_id)
        
        # Get session messages
        messages = session_manager.get_session(session_id)

        # Log the messages
        logging.info(f"Session messages: {messages}")
        
        # Construct the message list for OpenAI
        openai_messages = [
            {"role": "system", "content": "You are a helpful Plivo chatbot assistant. Answer the question and format the answer for chat widget based on the provided content."},
            {"role": "system", "content": f"Reference content: {truncated_content}"}
        ]
        
        # Add conversation history
        openai_messages.extend(messages)
        
        # Add the current query
        openai_messages.append({"role": "user", "content": query})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=openai_messages,
            max_tokens=250,
            temperature=0.4
        )
        
        answer = response.choices[0].message.content
        print(answer)
        # Fix the add_message calls by including session_id
        session_manager.add_message(session_id, "user", query)
        session_manager.add_message(session_id, "assistant", answer)
        
        return answer
    except Exception as e:
        return f"Error getting answer from OpenAI: {e}" 