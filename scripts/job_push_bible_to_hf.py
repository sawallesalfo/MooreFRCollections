import os
import pandas as pd
from datasets import Dataset

def list_parquet_files(directory):
    parquet_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".parquet"):
                parquet_files.append(os.path.join(root, file))
    return parquet_files

def read_parquet_files(parquet_files):
    """
    Read a list of Parquet files and concatenate valid ones , read all pd.read_parquet failed sometimes because corrupted files.
    """
    valid_dataframes = []
    for file in parquet_files:
        try:
            # Attempt to read the Parquet file
            df = pd.read_parquet(file)
            valid_dataframes.append(df)
        except Exception as e:
            print(f"Failed to read {file}. Error: {e}")

    if valid_dataframes:
        concatenated_df = pd.concat(valid_dataframes, ignore_index=True)
        return concatenated_df
    else:
        print("No valid Parquet files found.")
        return None

directory_path = "datasets/bible_data_moore.parquet/"
parquet_files = list_parquet_files(directory_path)
result_df_moore = read_parquet_files(parquet_files)

dataset = Dataset.from_pandas(result_df_moore)
dataset.push_to_hub("MooreFRCollections_BibleOnlyText", commit_message="🚀 publish bible text moore trans")