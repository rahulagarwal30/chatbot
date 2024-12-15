import pusher
from ...config.config import PUSHER_CONFIG

pusher_client = pusher.Pusher(**PUSHER_CONFIG)

def send_message(message):
    pusher_client.trigger('my-channel', 'event-bot-response', {'message': message}) 