from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time
import logging
from ...config.config import SESSION_TIMEOUT_MINUTES, SESSION_MESSAGE_LIMIT
from threading import RLock

class SessionError(Exception):
    """Base exception class for session-related errors"""
    pass

class SessionManager:
    def __init__(self, session_timeout_minutes=SESSION_TIMEOUT_MINUTES, message_limit=SESSION_MESSAGE_LIMIT):
        try:
            self.sessions: Dict[str, dict] = {}
            self.session_timeout = timedelta(minutes=session_timeout_minutes)
            self.message_limit = message_limit
            self.lock = RLock()
            
            # Start cleanup thread
            self.cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions, daemon=True)
            self.cleanup_thread.start()
        except Exception as e:
            logging.error(f"Failed to initialize SessionManager: {str(e)}")
            raise SessionError(f"Session manager initialization failed: {str(e)}")

    def _cleanup_expired_sessions(self):
        """Periodically clean up expired sessions"""
        while True:
            try:
                current_time = datetime.now()
                with self.lock:
                    # Find and remove expired sessions
                    expired_sessions = [
                        session_id for session_id, session in self.sessions.items()
                        if current_time - session['last_access'] > self.session_timeout
                    ]
                    
                    # Remove expired sessions
                    for session_id in expired_sessions:
                        del self.sessions[session_id]
                        logging.info(f"Cleaned up expired session: {session_id}")
                
                # Check every minute for expired sessions
                time.sleep(60)
            except Exception as e:
                logging.error(f"Error in cleanup thread: {str(e)}")
                time.sleep(60)

    def get_session(self, session_id: str) -> List[dict]:
        """Get or create a session for the given session_id"""
        if not isinstance(session_id, str):
            raise SessionError("Session ID must be a string")
            
        try:
            with self.lock:
                current_time = datetime.now()
                
                # Check if session exists and is still valid
                if session_id in self.sessions:
                    session = self.sessions[session_id]
                    # If session has expired, clear messages
                    if current_time - session['last_access'] > self.session_timeout:
                        session['messages'] = []
                    session['last_access'] = current_time
                    return session['messages']
                
                # Create new session if it doesn't exist
                self.sessions[session_id] = {
                    'messages': [],
                    'last_access': current_time
                }
                return self.sessions[session_id]['messages']
        except Exception as e:
            logging.error(f"Error getting session {session_id}: {str(e)}")
            raise SessionError(f"Failed to get session: {str(e)}")

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to the session history"""
        if not isinstance(session_id, str):
            raise SessionError("Session ID must be a string")
        if not isinstance(role, str):
            raise SessionError("Role must be a string")
        if not isinstance(content, str):
            raise SessionError("Content must be a string")
            
        try:
            with self.lock:
                messages = self.get_session(session_id)
                messages.append({"role": role, "content": content})
                # Keep only last N messages to prevent context from getting too large
                if len(messages) > self.message_limit:
                    messages.pop(0)
                # Update last access time
                self.sessions[session_id]['last_access'] = datetime.now()
        except Exception as e:
            logging.error(f"Error adding message to session {session_id}: {str(e)}")
            raise SessionError(f"Failed to add message: {str(e)}")

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists for the given session_id"""
        if not isinstance(session_id, str):
            raise SessionError("Session ID must be a string")
            
        try:
            return session_id in self.sessions
        except Exception as e:
            logging.error(f"Error checking session existence {session_id}: {str(e)}")
            raise SessionError(f"Failed to check session existence: {str(e)}")

    def create_session(self, session_id: str) -> None:
        """Create a new session"""
        if not isinstance(session_id, str):
            raise SessionError("Session ID must be a string")
            
        try:
            with self.lock:
                if not self.session_exists(session_id):
                    self.sessions[session_id] = {
                        'messages': [],
                        'last_access': datetime.now()
                    }
        except Exception as e:
            logging.error(f"Error creating session {session_id}: {str(e)}")
            raise SessionError(f"Failed to create session: {str(e)}")

    def clear_session(self, session_id: str) -> None:
        """Clear all messages from a session"""
        if not isinstance(session_id, str):
            raise SessionError("Session ID must be a string")
        
        try:
            with self.lock:
                if session_id in self.sessions:
                    self.sessions[session_id]['messages'] = []
                    self.sessions[session_id]['last_access'] = datetime.now()
        except Exception as e:
            logging.error(f"Error clearing session {session_id}: {str(e)}")
            raise SessionError(f"Failed to clear session: {str(e)}")

# Create singleton instance with default configuration
try:
    session_manager = SessionManager()
except Exception as e:
    logging.critical(f"Failed to create SessionManager instance: {str(e)}")
    raise 