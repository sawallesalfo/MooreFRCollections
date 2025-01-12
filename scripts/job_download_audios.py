import os
import boto3
from loguru import logger
from urllib.parse import quote

from jwsoup.audio.scraper import download_audios

encoded_key = quote("Yel-bũnã/page_28.mp3")

# Configuration - downloads audios
start_url = "https://www.jw.org/mos/d-s%E1%BA%BDn-yiisi/biible/nwt/books/Yel-b%C5%A9n%C3%A3/28"
output_dir = "audio_files"
max_file_size = 2

logger.info("Downloading audios...")
download_audios(start_url, output_dir, max_file_size)
logger.info(f"Audio files downloaded to {output_dir}")

# Configuration - environnement S3
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
endpoint_url = os.getenv('AWS_ENDPOINT_URL_S3')
region = os.getenv('AWS_REGION')

print("aaaaaaaaaaa", region)

# Initialisation  S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
    region_name=region
)

bucket_name = "moore-collection"
s3_prefix = "raw_data/"

def upload_folder_to_s3(folder_path, bucket_name, s3_prefix):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            local_path = quote(os.path.join(root, file))
            relative_path = os.path.relpath(local_path, folder_path)
            s3_key = os.path.join(s3_prefix, relative_path)
            print("zzzzzzzzzzzz")
            print(s3_key, relative_path, local_path)
            s3_client.upload_file(local_path, bucket_name, s3_key)
            logger.info(f"Uploaded {local_path} to s3://{bucket_name}/{s3_key}")

logger.info(f"Uploading folder {output_dir} to S3...")
upload_folder_to_s3(output_dir, bucket_name, s3_prefix)
logger.info("Upload complete!")
