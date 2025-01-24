import os
from loguru import logger


def upload_file_to_s3(s3_client, local_path, bucket_name, s3_key):
    """Upload a single file to S3."""
    s3_client.upload_file(local_path, bucket_name, s3_key)
    logger.info(f"Uploaded {local_path} to s3://{bucket_name}/{s3_key}")


def download_file_from_s3(s3_client, bucket_name, s3_key, local_path):
    """Download a single file from S3."""
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    s3_client.download_file(bucket_name, s3_key, local_path)
    logger.info(f"Downloaded {s3_key} to {local_path}")


def list_s3_files(s3_client, bucket_name, prefix):
    """List all files in an S3 bucket under a given prefix."""
    paginator = s3_client.get_paginator("list_objects_v2")
    files = []
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get("Contents", []):
            files.append(obj["Key"])
    return files
