"""
Data from Masakhane
https://github.com/masakhane-io/lafand-mt/blob/main/data/json_files/fr-mos/train.json

Let's put Africa on the NLP map
""""

import os
import requests
import json
import pandas as pd
from datasets import Dataset
import boto3
from loguru import logger

def download_json_file(github_raw_url, local_file_path):
    """Downloads a JSON file from a GitHub raw URL."""
    try:
        response = requests.get(github_raw_url)
        response.raise_for_status()  
        with open(local_file_path, 'w', encoding='utf-8') as local_file:
            local_file.write(response.text)
        logger.success(f"Successfully downloaded JSON file to: {local_file_path}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading file from URL: {github_raw_url} - {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during download: {e}")
        return None

def parse_json_lines(file_path):
    """Parses a JSON file where each line is a JSON object."""
    french_texts = []
    moore_texts = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():  # Skip empty lines
                    try:
                        item = json.loads(line)
                        french_texts.append(item["translation"]["fr"])
                        moore_texts.append(item["translation"].get("mos", ""))
                    except json.JSONDecodeError as e:
                        logger.error(f"Error decoding JSON line: {line.strip()} - {e}")
    except FileNotFoundError:
        logger.error(f"Error: File not found at {file_path}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during parsing: {e}")
    return french_texts, moore_texts

def main():

    github_raw_urls = [
        "https://raw.githubusercontent.com/masakhane-io/lafand-mt/main/data/json_files/fr-mos/dev.json",
        "https://raw.githubusercontent.com/masakhane-io/lafand-mt/main/data/json_files/fr-mos/test.json",
        "https://raw.githubusercontent.com/masakhane-io/lafand-mt/main/data/json_files/fr-mos/train.json"
    ]

    all_french_texts = []
    all_moore_texts = []
    bucket_name="moore-collection"
    output_path = "hf_datasets/masakhane_fr_mos"
    
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    endpoint_url = os.getenv("AWS_ENDPOINT_URL_S3")
    if not all([access_key, secret_key]):
        raise ValueError("AWS credentials not configured")
    

    for i, url in enumerate(github_raw_urls):
        temp_file = f"temp_{i}.json"
        if download_json_file(url, temp_file):
            french, moore = parse_json_lines(temp_file)
            all_french_texts.extend(french)
            all_moore_texts.extend(moore)
            os.remove(temp_file)  # Clean up

    if all_french_texts:
        dataset = Dataset.from_dict({
            "french": all_french_texts,
            "moore": all_moore_texts,
            "source": ["masakhane-io"] * len(all_french_texts)
        })

        dataset.save_to_disk(
            f"s3://{bucket_name}/{output_path}",
            storage_options={
                "key": access_key,
                "secret": secret_key,
                "client_kwargs": {"endpoint_url": endpoint_url} if endpoint_url else {}
            }
        )

if __name__ == "__main__":
    main()
