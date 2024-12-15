import os
from dotenv import load_dotenv

load_dotenv()

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PUSHER_CONFIG = {
    'app_id': os.getenv("PUSHER_APP_ID"),
    'key': os.getenv("PUSHER_KEY"),
    'secret': os.getenv("PUSHER_SECRET"),
    'cluster': os.getenv("PUSHER_CLUSTER"),
    'ssl': True
}

# Configuration for file operations
FILE_AGE_DAYS = 2  # Number of days before re-fetching URL content
MAX_URLS_TO_PROCESS = -1  # -1 means process all URLs, positive number limits the count
