def filter_urls(urls):
    """Filter URLs that don't contain specific patterns"""
    excluded_patterns = [
        'blog',
        'video',
        'docs',
        'virtual-phone-numbers/pricing',
        'virtual-phone-numbers/coverage',
        'sip-trunking/pricing',
        'sip-trunking/coverage',
        'voice/pricing',
        'voice/coverage',
        'sms/pricing',
        'sms/coverage',
        'sms/coverage-trunking/pricing',
        'sms/coverage-trunking/coverage'
    ]
    
    filtered_urls = [
        url for url in urls 
        if not any(pattern in url.lower() for pattern in excluded_patterns)
    ]
    return filtered_urls 