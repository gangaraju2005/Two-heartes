import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
import logging
from core.config import settings

logger = logging.getLogger(__name__)

import os

# Initialize Firebase Admin SDK
try:
    # Try to find a service account file in the current directory
    service_account_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "firebase-service-account.json")
    
    if os.path.exists(service_account_path):
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        logger.info(f"Firebase Admin SDK initialized using certificate: {service_account_path}")
    else:
        # Fallback to default credentials (works on Google Cloud or if GOOGLE_APPLICATION_CREDENTIALS env is set)
        firebase_admin.initialize_app(options={
            'projectId': settings.FIREBASE_PROJECT_ID or 'showgo-d993b',
        })
        logger.info("Firebase Admin SDK initialized using default credentials")
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
