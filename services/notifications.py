from typing import List, Dict, Any
import logging
from expo_push_sdk import PushClient, PushMessage
from core.config import settings

logger = logging.getLogger(__name__)

def send_push_notifications(tokens: List[str], title: str, body: str, data: Dict[str, Any] = None):
    """
    Send push notifications using Expo Push SDK.
    """
    if not tokens:
        return

    client = PushClient()
    messages = [
        PushMessage(to=token, title=title, body=body, data=data) 
        for token in tokens if token.startswith('ExponentPushToken')
    ]

    try:
        results = client.publish(messages)
        logger.info(f"Push notifications sent to {len(messages)} devices")
        return results
    except Exception as e:
        logger.error(f"Failed to send push notifications: {e}")
        return None
