import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Move all imports here
from src.crawler.sitemap_crawler import crawl_sitemap   
from src.crawler.url_processor import filter_urls
from src.crawler.file_operations import save_and_index_url_content, delete_all_documents_from_es
from src.config.config import MAX_URLS_TO_PROCESS
from elasticsearch import Elasticsearch
import time

def main():
    # Initialize Elasticsearch client
    es = Elasticsearch("http://localhost:9200")

    #delete all documents from elasticsearch
    #delete_all_documents_from_es()

    #print document count in elastic search
    print(f"Document count in elastic search: {es.count(index='url_content')}")
    # Check if Elasticsearch is running
    if not es.ping():
        print("Error: Could not connect to Elasticsearch. Make sure it's running.")
        return
    
    try:
        # Get URLs from sitemap
        sitemap_url = "https://www.plivo.com/sitemap.xml"
        print(f"Fetching URLs from {sitemap_url}...")
        urls = crawl_sitemap(sitemap_url)
        print(f"Found {len(urls)} URLs in sitemap")
        
        # Filter URLs
        filtered_urls = filter_urls(urls)
        print(f"Filtered down to {len(filtered_urls)} URLs")
        
        # Process URLs based on configuration
        urls_to_process = filtered_urls if MAX_URLS_TO_PROCESS == -1 else filtered_urls[:MAX_URLS_TO_PROCESS]
        total_urls = len(urls_to_process)
        
        for index, url in enumerate(urls_to_process):
            print(f"Processing {index + 1}/{total_urls}: {url}")
            save_and_index_url_content(url, index)
            #print(f"Document count in elastic search: {es.count(index='url_content')}")
            
        print("Crawling and indexing completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 