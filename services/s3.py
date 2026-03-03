import boto3
from botocore.exceptions import ClientError
from core.config import settings
import uuid
import logging

logger = logging.getLogger(__name__)


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )


def upload_image(file_bytes: bytes, filename: str, folder: str = "general", content_type: str = "image/jpeg") -> str:
    """
    Upload image bytes to S3 and return the public URL.
    folder: 'profiles', 'movies', etc.
    """
    s3 = get_s3_client()
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
    key = f"{folder}/{uuid.uuid4().hex}.{ext}"

    try:
        s3.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )
        url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        logger.info(f"Uploaded image to S3: {key}")
        return url
    except ClientError as e:
        logger.error(f"S3 upload failed: {e}")
        raise Exception(f"Failed to upload image: {str(e)}")


def delete_image(key: str) -> bool:
    """Delete an image from S3 by its key."""
    s3 = get_s3_client()
    try:
        s3.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
        return True
    except ClientError as e:
        logger.error(f"S3 delete failed: {e}")
        return False


def get_key_from_url(url: str) -> str:
    """Extract S3 key from a full S3 URL."""
    prefix = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/"
    if url.startswith(prefix):
        return url[len(prefix):]
    return ""
