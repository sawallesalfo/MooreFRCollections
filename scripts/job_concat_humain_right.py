import pandas as pd
import json
from pathlib import Path
from datasets import load_dataset

# concat all jsons
dictionnary_path= "./declaration droits humains"
jsonpaths = list(Path(dictionnary_path).glob("*.json"))
data = []
for jsonpath in (jsonpaths):
    print(jsonpath)
    with open(jsonpath, encoding="utf-8") as f:
        jsonfile = json.load(f)
        data.append(pd.DataFrame(jsonfile).assign(source="declaration droits humains"))

dictionnary = pd.concat(data).reset_index(drop=True).rename(columns={"français":"french"})

# # Concat with the previous datasets
previous_dataset = pd.read_parquet(r"C:\Users\sawal\OneDrive\Bureau\Projets X\datasets\datasets\dictionnary Index Français Moore.parquet")
dataset = pd.concat([previous_dataset, dictionnary], ignore_index=True)
dataset.to_parquet("datasets.parquet")

# # push to hugginface
dataset = load_dataset("parquet", data_files="datasets.parquet")
dataset.push_to_hub("MooreFRCollections", commit_message=f"add {dictionnary_path}")

