import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
import os
from bs4 import BeautifulSoup
import re
import time

def crawl_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse XML content
        root = ET.fromstring(response.content)
        
        # Since it works without namespace, we can simplify this part
        urls = []
        
        # Check if this is a sitemap index
        sitemap_tags = root.findall('sitemap')
        if sitemap_tags:
            print(f"\nFound sitemap index with {len(sitemap_tags)} sub-sitemaps")
            for sitemap in sitemap_tags:
                loc = sitemap.find('loc')
                if loc is not None and loc.text:
                    print(f"\nProcessing sub-sitemap: {loc.text}")
                    sub_urls = crawl_sitemap(loc.text)
                    urls.extend(sub_urls)
        
        # Try as regular sitemap
        if not urls:
            url_tags = root.findall('url')
            if url_tags:
                print(f"\nFound regular sitemap with {len(url_tags)} URLs")
                for url in url_tags:
                    loc = url.find('loc')
                    if loc is not None and loc.text:
                        print(f"Found URL: {loc.text}")
                        urls.append(loc.text)
        
        # If still no URLs found, try direct children
        if not urls:
            print("\nTrying direct children approach...")
            for child in root:
                if 'loc' in child.tag:
                    print(f"Found URL via direct children: {child.text}")
                    urls.append(child.text)
        
        return urls

    except requests.RequestException as e:
        print(f"\nError fetching sitemap: {e}")
        return []
    except ET.ParseError as e:
        print(f"\nError parsing XML: {e}")
        print(f"Response content: {response.text[:200]}...")  # Print first 200 chars of response
        return []

def filter_urls(urls):
    """
    Filter URLs that don't contain 'blog' or 'video' in them
    
    Args:
        urls (list): List of URL strings
        
    Returns:
        list: Filtered URLs
    """
    filtered_urls = [
        url for url in urls 
        if 'blog' not in url.lower() 
        and 'video' not in url.lower()
        #and 'docs' not in url.lower()
        and 'virtual-phone-numbers/pricing' not in url.lower()
        and 'virtual-phone-numbers/coverage' not in url.lower()
        and 'sip-trunking/pricing' not in url.lower()
        and 'sip-trunking/coverage' not in url.lower()
        and 'voice/pricing' not in url.lower()
        and 'voice/coverage' not in url.lower()
        and 'sms/pricing' not in url.lower()
        and 'sms/coverage' not in url.lower()
        and 'sms/coverage-trunking/pricing' not in url.lower()
        and 'sms/coverage-trunking/coverage' not in url.lower()
    ]
    return filtered_urls

def clean_html_content(html_content):
    """
    Clean HTML content by removing tags, CSS, scripts, while preserving logical line breaks
    
    Args:
        html_content (str): Raw HTML content
        
    Returns:
        str: Cleaned text content with preserved structure
    """
    # Create BeautifulSoup object
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted elements
    for script in soup(["script", "style", "header", "footer", "nav"]):
        script.decompose()
    
    # Replace only major block elements with line breaks
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
        tag.append('\n')
    
    # Handle lists specially - add newline only after list items
    for li in soup.find_all('li'):
        if not any(parent.name == 'nav' for parent in li.parents):
            li.append('\n')
    
    # Get text content
    text = soup.get_text()
    
    # Clean up whitespace while preserving line breaks
    lines = [line.strip() for line in text.splitlines()]
    text = '\n'.join(line for line in lines if line)
    
    # Remove excessive line breaks (more than 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text

def save_url_content(url, index):
    """
    Fetch URL content, clean it, and save to a file in the url_content directory
    Only fetches new content if the existing file is older than 48 hours or URL has changed
    
    Args:
        url (str): URL to fetch
        index (int): Index number for the filename
    """
    # Create url_content directory if it doesn't exist
    os.makedirs('url_content', exist_ok=True)
    
    # Create filename from URL
    content_filename = os.path.join('url_content', f"url_content_{index}.txt")
    url_filename = os.path.join('url_content', f"url_{index}.txt")
    
    # Check if files exist and URL matches
    should_fetch = True
    if os.path.exists(content_filename) and os.path.exists(url_filename):
        file_age = time.time() - os.path.getmtime(content_filename)
        
        # Read the stored URL
        with open(url_filename, 'r', encoding='utf-8') as f:
            stored_url = f.read().strip()
            
        # Only skip if URL matches and content is fresh
        if url == stored_url and file_age < 7 * 24 * 3600:  # 7 days in seconds
            print(f"Skipping {url} - content is less than 7 days old")
            should_fetch = False
    
    if should_fetch:
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Clean the HTML content
            cleaned_content = clean_html_content(response.text)
            
            # Save the content
            with open(content_filename, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
                
            # Save the URL
            with open(url_filename, 'w', encoding='utf-8') as f:
                f.write(url)
                
            print(f"Saved cleaned content from {url} to {content_filename}")
                
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
        except IOError as e:
            print(f"Error saving file for {url}: {e}")

def delete_content_files():
    """
    Delete the URL content files and their directory
    """
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

def main():
    sitemap_url = 'https://www.plivo.com/sitemap.xml'
    urls = crawl_sitemap(sitemap_url)
    filtered_urls = filter_urls(urls)

    print(f"\nFound {len(filtered_urls)} URLs:")

    
    # Save content from first 1200 URLs
    print("\nFetching and saving content from first 1200 URLs...")
    for i, url in enumerate(filtered_urls[:1200], 1):
        save_url_content(url, i)

    # Delete the content files
    #delete_content_files()

if __name__ == '__main__':
    main() 

    