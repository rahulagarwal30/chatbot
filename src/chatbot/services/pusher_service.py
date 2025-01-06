import pusher
import logging
from ...config.config import PUSHER_CONFIG, PUSHER_CHANNEL

pusher_client = pusher.Pusher(**PUSHER_CONFIG)

def send_message(message):
    pusher_client.trigger(PUSHER_CHANNEL, 'event-bot-response', {'message': message}) 