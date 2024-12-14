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
                        #print(f"Found URL: {loc.text}")
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
        print(f"Response content: {response.text[:200]}...")
        return [] 