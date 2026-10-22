
import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

s3_client = boto3.client(
    "s3",
    endpoint_url=os.getenv("S3_ENDPOINT_URL"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
)


def create_bucket():
    bucket_name = os.getenv("S3_BUCKET_NAME")

    existing_buckets = s3_client.list_buckets()["Buckets"]

    if not any(bucket["Name"] == bucket_name for bucket in existing_buckets):
        s3_client.create_bucket(Bucket=bucket_name)

    return f"Bucket '{bucket_name}' is ready."


def upload_archive(file_path):
    bucket_name = os.getenv("S3_BUCKET_NAME")
    path = Path(file_path)

    s3_client.upload_file(
        str(path),
        bucket_name,
        path.name,
    )

    return f"Uploaded {path.name} to {bucket_name}"
