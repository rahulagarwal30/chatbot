import pusher
from config.config import PUSHER_CONFIG

pusher_client = pusher.Pusher(
    app_id=PUSHER_CONFIG['app_id'],
    key=PUSHER_CONFIG['key'],
    secret=PUSHER_CONFIG['secret'],
    cluster=PUSHER_CONFIG['cluster'],
    ssl=PUSHER_CONFIG['ssl']
)

def send_message(message):
    """Send message through Pusher"""
    pusher_client.trigger('my-channel', 'event-bot-response', {'message': message})
