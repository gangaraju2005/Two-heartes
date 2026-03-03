import boto3
import logging
from core.config import settings

logger = logging.getLogger(__name__)


async def send_otp_sms(mobile: str, otp: int) -> bool:
    """
    Send OTP via AWS SNS.
    Returns True if SMS was sent successfully.
    """
    if not settings.AWS_ACCESS_KEY_ID or settings.AWS_ACCESS_KEY_ID == "your-access-key-id":
        logger.warning(f"AWS credentials not configured. OTP for {mobile}: {otp}")
        return False

    # Ensure phone number is in E.164 format (required by SNS)
    phone = mobile.strip()
    if not phone.startswith("+"):
        if phone.startswith("91") and len(phone) > 10:
            phone = "+" + phone
        else:
            phone = "+91" + phone

    try:
        sns = boto3.client(
            "sns",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION or "ap-south-1",  # Mumbai region is best for India
        )

        sns.publish(
            PhoneNumber=phone,
            Message=f"Your ShowGO OTP is {otp}. Do not share this with anyone.",
            MessageAttributes={
                "AWS.SNS.SMS.SenderID": {
                    "DataType": "String",
                    "StringValue": "ShowGO",
                },
                "AWS.SNS.SMS.SMSType": {
                    "DataType": "String",
                    "StringValue": "Transactional",  # Higher priority than Promotional
                },
            },
        )
        logger.info(f"SNS OTP sent to {phone}")
        return True

    except Exception as e:
        logger.error(f"AWS SNS failed to send SMS: {e}")
        return False
