from sitemap_crawler import crawl_sitemap   
from url_processor import filter_urls
from file_operations import save_and_index_url_content, delete_content_files, delete_all_documents_from_es
from elasticsearch import Elasticsearch
from config.config import MAX_URLS_TO_PROCESS
import time

def main():
    # Initialize Elasticsearch client
    es = Elasticsearch("http://localhost:9200")
    
    # Check if Elasticsearch is running
    if not es.ping():
        print("Error: Could not connect to Elasticsearch. Make sure it's running.")
        return

    
    try:
        # Delete existing content files (optional cleanup)
        #delete_content_files()
        #Delete all documents in the index
        #delete_all_documents_from_es()
        
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
            # Add a small delay to avoid overwhelming the server
            #time.sleep(1)
            
        print("Crawling and indexing completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 