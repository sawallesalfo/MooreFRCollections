import os
from datasets import load_dataset, load_from_disk, concatenate_datasets, Features, Value, Dataset, DownloadConfig
from loguru import logger

def process_dataset(current_dataset_path, incoming_dataset_path, output_dataset_path, storage_options, hf_token, commit_message):
    """
    Charge, sélectionne les colonnes attendues, fusionne deux datasets audio, puis pousse le résultat sur le Hub Hugging Face
    
    Args:
        current_dataset_path (str): Chemin du dataset actuel sur Hugging Face Hub.
        incoming_dataset_path (str): Chemin du nouveau dataset à intégrer.
        output_dataset_path (str): Chemin du dataset final (Hub).
        storage_options (dict): Options pour accéder au stockage distant.
        hf_token (str): Jeton d'authentification Hugging Face.
        commit_message (str): Message de commit pour le push sur le Hub.

    Returns:
        None
    """
    logger.info("Chargement du dataset actuel depuis le Hub...")
    current_dataset = load_dataset(
        current_dataset_path,
        split="train",
        download_config=DownloadConfig(token=hf_token)
    )
    
    logger.info("Chargement du dataset entrant depuis le stockage...")
    incoming_dataset = load_from_disk(incoming_dataset_path, storage_options=storage_options)
    
    # Définition des colonnes attendues
    expected_features = Features({
        "french": Value("string"),
        "moore": Value("string"),
        "source": Value("string"),
    })
    
    # Filtrage des colonnes du dataset entrant
    incoming_dataset = incoming_dataset.remove_columns(
        [col for col in incoming_dataset.column_names if col not in expected_features]
    )
    
    logger.info("Sélection des colonnes réussie ✅")
    logger.info(f"Nombre de lignes - Dataset actuel: {len(current_dataset)}, Dataset entrant: {len(incoming_dataset)}")
    
    final_dataset = concatenate_datasets([current_dataset, incoming_dataset])
    logger.info("Fusion des datasets réussie ✅")
    
    logger.info(f"Push du dataset final sur {output_dataset_path}...")
    final_dataset.push_to_hub(output_dataset_path, commit_message=commit_message)
    logger.info("Push terminé avec succès ✅")

if __name__ == "__main__":
    BUCKET_NAME = "moore-collection"
    
    ########################## Change me ######################################
    CURRENT_DATASET_PATH = "sawadogosalif/MooreFRCollections"
    COMMIT_MESSAGE = "🚀 Add masakhane dataset"
    INCOMING_DATASET_PATH = f"s3://{BUCKET_NAME}/hf_datasets/masakhane_fr_mos"
    OUTPUT_DATASET_PATH = CURRENT_DATASET_PATH
    ############################################################################
    
    storage_options = {
        "key": os.getenv("AWS_ACCESS_KEY_ID"),
        "secret": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "client_kwargs": {"endpoint_url": os.getenv("AWS_ENDPOINT_URL_S3")}
    }
    
    HF_TOKEN = os.getenv("HF_TOKEN")
    
    process_dataset(
        CURRENT_DATASET_PATH,
        INCOMING_DATASET_PATH,
        OUTPUT_DATASET_PATH,
        storage_options,
        HF_TOKEN,
        COMMIT_MESSAGE
    )
