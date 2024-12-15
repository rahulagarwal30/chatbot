import os
import requests
from src.crawler.html_cleaner import clean_html_content
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from ..config.config import FILE_AGE_DAYS

# Initialize Elasticsearch client and BERT model
es = Elasticsearch("http://localhost:9200")
model = SentenceTransformer('all-MiniLM-L6-v2')

def save_and_index_url_content(url, index):
    """Fetch URL content, clean it, and save to file and Elasticsearch"""
    os.makedirs('url_content', exist_ok=True)
    
    content_filename = os.path.join('url_content', f"url_content_{index}.txt")
    url_filename = os.path.join('url_content', f"url_{index}.txt")
    
    should_fetch = True
    if os.path.exists(content_filename) and os.path.exists(url_filename):
        with open(url_filename, 'r', encoding='utf-8') as f:
            stored_url = f.read().strip()
            
        if url == stored_url:
            print(f"Skipping {url} - content already exists")
            should_fetch = False
    
    if should_fetch:
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            cleaned_content = clean_html_content(response.text)
            
            # Save to files
            with open(content_filename, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
                
            with open(url_filename, 'w', encoding='utf-8') as f:
                f.write(url)
            
            # Generate vector embedding
            vector = model.encode(cleaned_content)
            
            # Index in Elasticsearch
            doc = {
                'url': url,
                'content': cleaned_content,
                'content_vector': vector.tolist()
            }
            
            es.index(index='url_content', id=str(index), document=doc)
            print(f"Saved and indexed content from {url}")
                
        except Exception as e:
            print(f"Error processing {url}: {e}")

def delete_content_files():
    """Delete the URL content files and their directory"""
    try:
        if os.path.exists('url_content'):
            for file in os.listdir('url_content'):
                os.remove(os.path.join('url_content', file))
            os.rmdir('url_content')
    except Exception as e:
        print(f"Error deleting files: {e}")

def delete_all_documents_from_es():
    try:
        es.delete_by_query(index="url_content", body={"query": {"match_all": {}}})
        print('All documents deleted')
    except Exception as e:
        print(f'Error deleting documents: {e}') 