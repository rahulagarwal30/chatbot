from openai import OpenAI
from ...config.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_answer_from_openai(query, content):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful chatbot assistant. Answer the question and format the answer for chat widget based on the provided content."},
                {"role": "user", "content": f"Based on this content: {content}\n\nAnswer this question: {query}"}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting answer from OpenAI: {e}" 