from bs4 import BeautifulSoup
import re

def clean_html_content(html_content):
    """Clean HTML content by removing tags, CSS, scripts, while preserving logical line breaks"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted elements
    for script in soup(["script", "style", "header", "footer", "nav"]):
        script.decompose()
    
    # Replace block elements with line breaks
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
        tag.append('\n')
    
    # Handle lists
    for li in soup.find_all('li'):
        if not any(parent.name == 'nav' for parent in li.parents):
            li.append('\n')
    
    # Get and clean text content
    text = soup.get_text()
    lines = [line.strip() for line in text.splitlines()]
    text = '\n'.join(line for line in lines if line)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text 