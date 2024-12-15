import os
import time
import requests
from html_cleaner import clean_html_content
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import torch
from config.config import FILE_AGE_DAYS

# Initialize Elasticsearch client and BERT model
es = Elasticsearch("http://localhost:9200")  # Adjust URL as needed
model = SentenceTransformer('all-MiniLM-L6-v2')


def save_and_index_url_content(url, index):
    """Fetch URL content, clean it, and save to file and Elasticsearch"""
    os.makedirs('url_content', exist_ok=True)
    
    #print the count of documents in the index
    print('Document count: ', es.count(index="url_content")['count'])


    content_filename = os.path.join('url_content', f"url_content_{index}.txt")
    url_filename = os.path.join('url_content', f"url_{index}.txt")
    
    should_fetch = True
    if os.path.exists(content_filename) and os.path.exists(url_filename):
        file_age = time.time() - os.path.getmtime(content_filename)
        
        with open(url_filename, 'r', encoding='utf-8') as f:
            stored_url = f.read().strip()
            
        if url == stored_url and file_age < FILE_AGE_DAYS * 24 * 3600:
            print(f"Skipping {url} - content is less than {FILE_AGE_DAYS} days old")
            should_fetch = False

    #should_fetch = True
    
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
                'content_vector': vector.tolist(),
                'timestamp': time.time()
            }
            
            es.index(index='url_content', id=str(index), document=doc)
            print(f"Saved and indexed content from {url}")
                
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
        except IOError as e:
            print(f"Error saving file for {url}: {e}")
        except Exception as e:
            print(f"Error processing content for {url}: {e}")

def delete_content_files():
    """Delete the URL content files and their directory"""
    try:
        if os.path.exists('url_content'):
            for file in os.listdir('url_content'):
                file_path = os.path.join('url_content', file)
                try:
                    os.remove(file_path)
                    print(f"Deleted {file_path}")
                except OSError as e:
                    print(f"Error deleting {file_path}: {e}")
            os.rmdir('url_content')
            print("Deleted url_content directory")
    except OSError as e:
        print(f"Error handling url_content directory: {e}")

#method to delete all documents in the index
def delete_all_documents_from_es():
    try:
        es.delete_by_query(index="url_content", body={"query": {"match_all": {}}})
        print('All documents deleted')
    except Exception as e:
        print(f'Error deleting documents: {e}')
