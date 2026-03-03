import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
import logging
from core.config import settings

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK with project ID
try:
    firebase_admin.initialize_app(options={
        'projectId': settings.FIREBASE_PROJECT_ID or 'showgo-d993b',
    })
    logger.info("Firebase Admin SDK initialized successfully")
except ValueError:
    # Already initialized
    pass


def verify_firebase_token(id_token: str) -> dict:
    """
    Verify a Firebase ID token and return the decoded claims.
    Returns dict with 'phone_number', 'uid', etc.
    Raises Exception if token is invalid.
    """
    decoded_token = firebase_auth.verify_id_token(id_token)
    return decoded_token
