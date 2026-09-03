import boto3
from botocore.client import Config
from app.core.config import settings

# 1. Singleton variable to hold the S3 client
_s3_client = None


def get_s3_client():
    """
    Creates the S3 client once and reuses it.
    Creating a new client for every request is slow (DNS lookups, SSL handshakes).
    """
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,  # Points to our local MinIO
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version="s3v4"),  # REQUIRED for MinIO compatibility
        )
    return _s3_client


async def upload_file(
    key: str, file_data: bytes, content_type: str = "application/octet-stream"
):
    """
    Uploads raw bytes to S3/MinIO.
    key: The "path" inside the bucket, e.g., "screenshots/1/5.png"
    """
    client = get_s3_client()
    client.put_object(
        Bucket=settings.S3_BUCKET,
        Key=key,
        Body=file_data,
        ContentType=content_type,
    )
    return key


async def get_presigned_url(key: str, expiration: int = 3600) -> str:
    """
    Generates a temporary, secure URL to view/download the file.
    Expires in 1 hour (3600 seconds) by default.
    """
    client = get_s3_client()
    url = client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": key},
        ExpiresIn=expiration,
    )
    return url
