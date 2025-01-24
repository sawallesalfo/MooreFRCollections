import boto3

import os
from dotenv import load_dotenv

load_dotenv()


# Configuration - environnement S3
access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
endpoint_url = os.getenv("AWS_ENDPOINT_URL_S3")

# Initialisation  S3
s3_client = boto3.client(
    "s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
)


def delete_files_with_substring(bucket_name, substring):
    """
    Deletes all files in an S3 bucket that contain a specific substring in their key.

    :param bucket_name: Name of the S3 bucket.
    :param substring: Substring to match in the object keys.
    """

    paginator = s3_client.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=bucket_name)

    keys_to_delete = []

    for page in page_iterator:
        if "Contents" in page:
            for obj in page["Contents"]:
                if substring in obj["Key"]:
                    keys_to_delete.append({"Key": obj["Key"]})
                    if len(keys_to_delete) == 1000:
                        s3_client.delete_objects(
                            Bucket=bucket_name, Delete={"Objects": keys_to_delete}
                        )
                        keys_to_delete = []

    # Delete remaining keys (if any)
    if keys_to_delete:
        s3_client.delete_objects(Bucket=bucket_name, Delete={"Objects": keys_to_delete})

    print(f"Deleted all files containing '{substring}' in bucket '{bucket_name}'.")


bucket_name = "moore-collection"
delete_files_with_substring(bucket_name, "segmented_audios/page")
