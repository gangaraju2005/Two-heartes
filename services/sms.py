import httpx
import logging
from core.config import settings

logger = logging.getLogger(__name__)


async def send_otp_sms(mobile: str, otp: int) -> bool:
    """
    Send OTP via prioritized SMS providers.
    Currently uses AWS SNS.
    """
    # Fallback to AWS SNS
    if not settings.AWS_ACCESS_KEY_ID or settings.AWS_ACCESS_KEY_ID == "your-access-key-id":
        logger.warning(f"No SMS provider configured. OTP for {mobile}: {otp}")
        return False

    phone = mobile.strip()
    if not phone.startswith("+"):
        phone = f"+91{phone}" if len(phone) == 10 else f"+{phone}"

    try:
        import boto3
        sns = boto3.client(
            "sns",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION or "ap-south-1",
        )
        sns.publish(
            PhoneNumber=phone,
            Message=f"Your ShowGO OTP is {otp}. Do not share this with anyone.",
            MessageAttributes={
                "AWS.SNS.SMS.SenderID": {"DataType": "String", "StringValue": "ShowGO"},
                "AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": "Transactional"},
            },
        )
        logger.info(f"SNS OTP sent to {phone}")
        return True
    except Exception as e:
        logger.error(f"AWS SNS failed: {e}")
        return False
