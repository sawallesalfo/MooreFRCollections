import boto3
import os
from joblib import Parallel, delayed, parallel_backend
from functools import partial
import pandas as pd
from datasets import load_dataset
from loguru import logger
from openai import OpenAI

# Import helpers
from shelpers.data_parser import extract_audio_identifier
from shelpers.llm_utils import process_single_page
from shelpers.s3_utils import list_s3_files
from shelpers.global_vars import (
    BUCKET_NAME,
    SOURCE_FOLDER,
    SYSTEM_PROMPT,
    MODEL_NAME,
    BATCH_SIZE,
)

from dotenv import load_dotenv

load_dotenv("vars.env")

# Load dataset and proces
DATA_FILE = "sawadogosalif/MooreFRCollections_BibleOnlyText"
data = load_dataset(DATA_FILE, split="train").to_pandas()
data[["chapter", "page"]] = data["moore_source_url"].apply(
    lambda x: pd.Series(extract_audio_identifier(x))
)

# Clients configuration
access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
endpoint_url = os.getenv("AWS_ENDPOINT_URL_S3")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Collecting paths
logger.info("Collecting paths")
files = list_s3_files(s3_client, BUCKET_NAME, SOURCE_FOLDER)
segment_chapters = list(set([file.split("/")[1] for file in files]))

segment_path_dict = {
    segment_chapter: list_s3_files(
        s3_client, BUCKET_NAME, f"{SOURCE_FOLDER}/{segment_chapter}"
    )
    for segment_chapter in segment_chapters
}
logger.info("Segments and paths are ready.")


# Processing a single page 
def process_page(
    page_num, tmp, files, BUCKET_NAME, MODEL_NAME, SYSTEM_PROMPT, BATCH_SIZE
):
    try:
        tmp_page = tmp[tmp.page == page_num].reset_index(drop=True)
        logger.info(f"Processing page {page_num}")

        # Reinitialize clients inside the subprocess
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
        )
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Process page
        result = process_single_page(
            page_num,
            tmp_page,
            files,
            openai_client,
            s3_client,
            BUCKET_NAME,
            MODEL_NAME,
            SYSTEM_PROMPT,
            BATCH_SIZE,
        )
        print(f"Page {page_num} processed successfully.")
        return result
    except Exception as e:
        logger.error(f"Error processing page {page_num}: {e}")
        return None


def main(segment_path_dict, data, BUCKET_NAME, MODEL_NAME, SYSTEM_PROMPT):
    tasks = []

    segment_paths = segment_path_dict.items()

    for chapter, files in segment_paths:
        tmp = data[data.chapter == chapter]
        page_nums = tmp.page.unique()

        process_fn = partial(
            process_page,
            tmp=tmp,
            files=files,
            BUCKET_NAME=BUCKET_NAME,
            MODEL_NAME=MODEL_NAME,
            SYSTEM_PROMPT=SYSTEM_PROMPT,
            BATCH_SIZE=BATCH_SIZE,
        )

        # Add delayed tasks for parallel processing
        tasks.extend(delayed(process_fn)(page_num) for page_num in page_nums)

    # Execute all tasks in parallel
    logger.info("Starting parallel processing")
    with parallel_backend("loky", n_jobs=-1):
        results = Parallel()(tasks)


if __name__ == "__main__":
    main(segment_path_dict, data, BUCKET_NAME, MODEL_NAME, SYSTEM_PROMPT)
