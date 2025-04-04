# notifications/tasks.py
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_notification_task(room_id, notification_data):
    """
    Celery task to send a notification message to the specified room.
    Args:
        room_id (str): The room ID where the notification should be sent.
        notification_data (dict): Data to be included in the notification.
    """
    logger.debug(f"[TASK] Sending to chat_{room_id}: {notification_data}")
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"chat_{room_id}",
        {
            "type": "send_notification",
            "notification": notification_data,
        },
    )
