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