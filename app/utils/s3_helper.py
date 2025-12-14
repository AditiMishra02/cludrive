import boto3
import os
from datetime import datetime

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION")


s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
    endpoint_url=f"https://s3.{AWS_REGION}.amazonaws.com"
)


def upload_file_to_s3(file_stream, filename, user_id):
    # Give unique name to avoid collisions
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    s3_key = f"{user_id}/{timestamp}_{filename}"

    s3_client.upload_fileobj(
        file_stream,
        AWS_S3_BUCKET,
        s3_key,
        ExtraArgs={"ACL": "private"}  # keep file private
    )

    return s3_key


def generate_presigned_url(s3_key, expiry=3600):
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": AWS_S3_BUCKET, "Key": s3_key},
        ExpiresIn=expiry
    )
