import requests
import logging

def get_location_from_ip(ip_address):
    """Fetch location information from IP address"""
    try:
        # Skip localhost/private IPs
        if ip_address in ('127.0.0.1', 'localhost') or ip_address.startswith(('192.168.', '10.', '172.')):
            return 'Local development'
            
        # Use ipapi.co with rate limit handling
        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        if response.status_code == 200:
            data = response.json()
            # Check for rate limiting error
            if data.get('error') and 'rate limit' in data.get('reason', '').lower():
                return 'Rate limit exceeded'
            city = data.get('city', 'Unknown City')
            region = data.get('region', 'Unknown Region')
            country = data.get('country_name', 'Unknown Country')
            return f"{city}, {region}, {country}"
        return 'Location not found'
        
    except Exception as e:
        logging.error(f"Error getting location for IP {ip_address}: {str(e)}")
        return 'Location lookup failed'

__all__ = ['get_location_from_ip'] 