from openai import OpenAI
from ...config.config import OPENAI_API_KEY

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

def get_answer_from_openai(query, content):
    try:
        truncated_content = truncate_content(content)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful chatbot assistant. Answer the question and format the answer for chat widget based on the provided content."},
                {"role": "user", "content": f"Based on this content: {truncated_content}\n\nAnswer this question: {query}"}
            ],
            max_tokens=250,
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting answer from OpenAI: {e}" 