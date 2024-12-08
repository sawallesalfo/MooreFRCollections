import os
import pandas as pd
from datasets import Dataset


from jwsoup.text.utils import clean_text

def list_parquet_files(directory):
    """
    List all Parquet files in a directory recursively.
    """
    return [
        os.path.join(root, file)
        for root, _, files in os.walk(directory)
        for file in files if file.endswith(".parquet")
    ]

def read_parquet_files(parquet_files):
    """
    Read a list of Parquet files and concatenate valid ones.

    Parameters:
        parquet_files (list): List of Parquet file paths.

    Returns:
        pd.DataFrame or None: Concatenated DataFrame of valid files, or None if no valid files are found.
    """
    valid_dataframes = []
    for file in parquet_files:
        try:
            df = pd.read_parquet(file)
            valid_dataframes.append(df)
        except Exception as e:
            print(f"Failed to read {file}. Error: {e}")

    if valid_dataframes:
        return pd.concat(valid_dataframes, ignore_index=True)
    else:
        print("No valid Parquet files found.")
        return None

def process_dataset(directory, prefix):
    """
    Process a dataset by listing, reading, and cleaning Parquet files.

    Parameters:
        directory (str): Directory containing Parquet files.
        prefix (str): Prefix for the dataset columns.

    Returns:
        pd.DataFrame: Processed DataFrame with cleaned text and prefixed columns.
    """
    parquet_files = list_parquet_files(directory)
    df = read_parquet_files(parquet_files)

    if df is not None:
        df["verse_text"] = df["verse_text"].apply(clean_text)
        return df.add_prefix(prefix)
    else:
        return pd.DataFrame()

def merge_datasets(df1, df2, key1, key2):
    """
    Merge two datasets on specified keys and clean up the columns.

    Parameters:
        df1 (pd.DataFrame): First dataset.
        df2 (pd.DataFrame): Second dataset.
        key1 (str): Key column in the first dataset.
        key2 (str): Key column in the second dataset.

    Returns:
        pd.DataFrame: Merged dataset.
    """
    merged_df = (
        df1.merge(df2, left_on=key1, right_on=key2, how="inner")
           .drop_duplicates()
           .reset_index(drop=True)
           .rename(columns={key1: "verse_id"})
           .drop(columns=[key2])
    )
    return merged_df

# Process  Moore dataset
directory_moore = "datasets/bible_data_moore.parquet/"
moore_dataset = process_dataset(directory_moore, "moore_")

# Process  French dataset
directory_french = "datasets/bible_data_francais.parquet/"
french_dataset = process_dataset(directory_french, "french_")

# Merge
datasets = merge_datasets(moore_dataset, french_dataset, "moore_verse_id", "french_verse_id")
datasets.push_to_hub("MooreFRCollections_BibleOnlyText", commit_message=f"🚀 add moore with transcripts + metadata")
