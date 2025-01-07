import pusher
import logging
from ...config.config import PUSHER_CONFIG

pusher_client = pusher.Pusher(**PUSHER_CONFIG)

def send_message(message, device_id):
    channel = f"my-{device_id}"
    logging.info(f"Sending message to channel: {channel}")
    pusher_client.trigger(channel, 'event-bot-response', {'message': message}) 