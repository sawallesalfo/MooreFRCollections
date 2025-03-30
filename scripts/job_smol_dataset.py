"""
# SMOL : https://huggingface.co/datasets/google/smol

SMOL (Set for Maximal Overall Leverage) is a collection of professional
translations into 221 Low-Resource Languages, designed for training translation models
and increasing the representation of these languages in NLP and technology.

For further details, please refer to the SMOL Paper:
https://arxiv.org/abs/2502.12301
and the GATITOS Paper:
https://arxiv.org/abs/2303.15265
"""
import os
import re
import boto3
import pandas as pd
from datasets import load_dataset
from loguru import logger 
from dotenv import load_dotenv
from openai import OpenAI

def translate_to_west_african_french(query):
    """Translates English text to Western African French using OpenAI's GPT mode """
    
  
    client = OpenAI()
    
    system_prompt = """Tu es un traducteur de texte en anglas en français d'afrique occidentale.
    Tu dois juste donner la traduction. La réponse doit être entre la balise <text>.
    
    <example>
    User query: Hello
    Your answer: <text>Salut</text>
    User query: a
    Your answer : un
    </example>
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=1,
        top_p=1
    )
    
    output = response.choices[0].message.content
    
    translation_match = re.search(r'<text>(.*?)</text>', output, re.DOTALL)
    if translation_match:
        return translation_match.group(1).strip()
    return query

def process_gatitos():
    """
    Load and process the GATITOS dataset.
    Each example's target translations (in the 'trgs' field) is reduced to the first element.
    """
    ds = load_dataset("google/smol", "gatitos__en_mos", split="train").to_pandas()
    ds["trgs"]   = [value[0] for value in ds["trgs"] ]
    return ds

def process_smolsent():
    """
    Load and process the SmolSent dataset.
    """
    return load_dataset("google/smol", "smolsent__en_mos", split="train").to_pandas()

def process_smoldoc():
    """
    Load and process the SmolDoc dataset.
    Explodes the 'srcs' and 'trgs' lists into individual rows,
    merges them by aligned index, and assigns a source label.
    """
    ds = load_dataset("google/smol", "smoldoc__en_mos", split="train").to_pandas()
    ds_exploded = pd.merge(
        ds[["srcs"]].explode("srcs").reset_index(drop=True),
        ds[["trgs"]].explode("trgs").reset_index(drop=True),
        left_index=True,
        right_index=True
    ).assign(source="smol")
    return ds_exploded


def main():

    BUCKET_NAME = "moore-collection"
    OUTPUT_PATH = f"BurkimbIA/datasets/SMOL"
    
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    endpoint_url = os.getenv("AWS_ENDPOINT_URL_S3")
    
    if not all([access_key, secret_key, endpoint_url]):
        raise ValueError("AWS credentials ou endpoint URL non configurés")
    
    # Initialisation des clients S3
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint_url,
    )

    gatitos_df = process_gatitos()[["src", "trgs"]].rename(columns={"trgs": "moore"})
    smolsent_df = process_smolsent()[["src", "trg"]].rename(columns={"trg": "moore"})
    smoldoc_df = process_smoldoc()[["srcs", "trgs"]].rename(columns={"srcs": "src", "trgs": "moore"})
    logger.info(f"Gatitos length: {len(gatitos_df)}")
    logger.info(f"Smoldoc length: {len(smoldoc_df)}")
    logger.info(f"SmolSent length: {len(smolsent_df)}")

    combined_df = pd.concat([gatitos_df, smolsent_df, smoldoc_df]).assign(source="google/smol").head(10)
    combined_df["french"] = combined_df["src"].apply(translate_to_west_african_french)

    dataset = Dataset.from_pandas(x).remove_columns("__index_level_0__")
    dataset.save_to_disk(f"s3://{BUCKET_NAME}/{OUTPUT_PATH}",
    storage_options={"key": access_key, "secret": secret_key, "client_kwargs":{"endpoint_url":endpoint_url}},
    )
    
    logger.info(f"Dataset SMOL sauvegardé localement dans")
    return combined_df

if __name__ == "__main__":
  _ = main()
