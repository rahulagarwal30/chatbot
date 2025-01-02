import requests
import logging

def get_location_from_ip(ip_address):
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

def log_user_info(query: str, user_agent, ip_address, logger):
    """Log user information including device, location, and query details."""
    device_info = f"Browser: {user_agent.browser.family} {user_agent.browser.version_string}, "
    device_info += f"OS: {user_agent.os.family} {user_agent.os.version_string}, "
    device_info += f"Device: {user_agent.device.family}"
    
    logger.info(f"Received query: {query}")
    logger.info(f"User IP: {ip_address}")
    logger.info(f"Device Info: {device_info}")

__all__ = ['get_location_from_ip', 'log_user_info'] 