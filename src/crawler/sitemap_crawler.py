import requests
import xml.etree.ElementTree as ET

def crawl_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        urls = []
        
        # Check if this is a sitemap index
        sitemap_tags = root.findall('sitemap')
        if sitemap_tags:
            for sitemap in sitemap_tags:
                loc = sitemap.find('loc')
                if loc is not None and loc.text:
                    sub_urls = crawl_sitemap(loc.text)
                    urls.extend(sub_urls)
        
        # Try as regular sitemap
        if not urls:
            url_tags = root.findall('url')
            if url_tags:
                for url in url_tags:
                    loc = url.find('loc')
                    if loc is not None and loc.text:
                        urls.append(loc.text)
        
        return urls

    except Exception as e:
        print(f"Error processing sitemap: {e}")
        return [] 