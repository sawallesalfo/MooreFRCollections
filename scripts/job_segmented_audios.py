import os
from pathlib import Path
import boto3
from pydub import AudioSegment, silence
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# Configuration - environnement S3
access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
endpoint_url = os.getenv("AWS_ENDPOINT_URL_S3")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
)

# Utility Functions


def download_file_from_s3(bucket_name, s3_key, local_path):
    """Download a single file from S3."""
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    s3_client.download_file(bucket_name, s3_key, local_path)
    logger.info(f"Downloaded {s3_key} to {local_path}")


def process_audio_with_silence_detection(
    file_path, segment_folder, min_silence_len=400, silence_thresh=-35
):
    """
    Process an audio file to split it into segments based on detected silences.

    Args:
        file_path (str): Path to the input audio file.
        segment_folder (str): Folder to save the segmented audio files.
        min_silence_len (int): Minimum length of silence (in ms) to consider a split.
        silence_thresh (int): Silence threshold in dBFS.

    Returns:
        list: List of paths to the segmented audio files.
    """
    audio = AudioSegment.from_file(file_path)

    silences = silence.detect_silence(
        audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh
    )
    silences = [(start, end) for start, end in silences]

    start, segments = 0, []
    for i, (silence_start, silence_end) in enumerate(silences):
        segment = audio[start:silence_start]
        filename = f"{segment_folder}segment_{i+1}.mp3"
        segment.export(filename, format="mp3")
        logger.info(f"Segment saved: {filename}")
        start = silence_end
        segments.append(filename)
    return segments


def upload_file_to_s3(local_path, bucket_name, s3_key):
    """Upload a single file to S3."""
    s3_client.upload_file(local_path, bucket_name, s3_key)
    logger.info(f"Uploaded {local_path} to s3://{bucket_name}/{s3_key}")


def list_s3_files(bucket_name, prefix):
    """List all files in an S3 bucket under a given prefix."""
    paginator = s3_client.get_paginator("list_objects_v2")
    files = []
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get("Contents", []):
            files.append(obj["Key"])
    return files


def main():

    # Configuration
    bucket_name = "moore-collection"
    source_folder = "raw_data/Ebre-rãmbã"
    destination_folder = "fasoai-segmented_audios"
    local_download_folder = "downloaded_audio"

    files = list_s3_files(bucket_name, source_folder)#[137:]  # start from when it failed

    # Process each file
    for s3_key in files:
        # Skip folders
        if s3_key.endswith("/"):
            continue

        logger.info(f"Processing file: {s3_key}")
        try:
            # 1. Download the file
            suffix = s3_key.split("/")[-1].replace("\\", "/")
            local_file_path = f"{local_download_folder}/{suffix}"
            download_file_from_s3(bucket_name, s3_key, local_file_path)

            # 2. Process  file
            segment_subfolder = f"{destination_folder}/{local_file_path.split("downloaded_audio/")[-1].replace('.mp3', '')}/"
            os.makedirs(os.path.dirname(segment_subfolder), exist_ok=True)
            processed_segments = process_audio_with_silence_detection(
                local_file_path, segment_subfolder
            )

            # 3. Upload  processed segments
            for segment_path in processed_segments:
                upload_file_to_s3(segment_path, bucket_name, segment_path)

            logger.info(f"Completed processing for {s3_key}")

        except:
            logger.warning(f"processing of {s3_key} failed")


if __name__ == "__main__":
    main()
