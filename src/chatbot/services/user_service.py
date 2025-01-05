from datetime import datetime
from user_agents import parse
import uuid
import logging
from .location_service import get_location_from_ip

def collect_user_info(request, session, logger=None):
    """Collect and log user information from request"""
    user_info = {
        'query': request.json.get('message'),
        'user_agent': parse(request.headers.get('User-Agent', 'Unknown')),
        'ip_address': request.headers.get('X-Forwarded-For', request.remote_addr),
        'timestamp': datetime.now().isoformat(),
    }

    # Get or create session ID
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
    user_info['session_id'] = session_id

    # Get location if not already in session
    if 'location' not in session:
        try:
            location = get_location_from_ip(user_info['ip_address'])
            session['location'] = location
            user_info['location'] = location
        except Exception as e:
            if logger:
                logger.error(f"Error getting location for IP {user_info['ip_address']}: {str(e)}")
            user_info['location'] = 'Unknown'
    else:
        user_info['location'] = session['location']

    # Log all user information together
    log_message = (
        f"Query: {user_info['query']} | "
        f"IP: {user_info['ip_address']} | "
        f"Location: {user_info['location']} | "
        f"User Agent: {user_info['user_agent']} | "
        f"Session ID: {user_info['session_id']}"
    )
    if logger:
        logger.info(log_message)
    
    # Log detailed user info
    log_user_info(
        query=user_info['query'],
        user_agent=user_info['user_agent'],
        ip_address=user_info['ip_address'],
        logger=logger
    )

    return user_info

def log_user_info(query: str, user_agent, ip_address, logger):
    """Log user information including device, location, and query details."""
    device_info = f"Browser: {user_agent.browser.family} {user_agent.browser.version_string}, "
    device_info += f"OS: {user_agent.os.family} {user_agent.os.version_string}, "
    device_info += f"Device: {user_agent.device.family}"
    
    logger.info(f"Received query: {query}")
    logger.info(f"User IP: {ip_address}")
    logger.info(f"Device Info: {device_info}")

__all__ = ['collect_user_info', 'log_user_info'] 