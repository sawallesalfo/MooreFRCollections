import pandas as pd
import json
from pathlib import Path
from datasets import load_dataset

# concat all jsons
dictionnary_path= "./Dictionnary Edition Janvier 2017, Compilé par Urs Niggli"
jsonpaths = list(Path(dictionnary_path).glob("*.json"))
data = []
for jsonpath in (jsonpaths):
    print(jsonpath)
    with open(jsonpath, encoding="utf-8") as f:
        jsonfile = json.load(f)
        cleaned_list = [x for x in jsonfile if x is not None]
        data.append(pd.DataFrame(sum(cleaned_list, [])).assign(source="dictionnary-Urs Niggli-Edition Janvier 2017"))

dictionnary = pd.concat(data).reset_index(drop=True).rename(columns={"français":"french"})

# Concat with the previous datasets
previous_dataset = pd.read_parquet("datasets.parquet")
dataset = pd.concat([previous_dataset, dictionnary], ignore_index=True)
dataset.to_parquet("datasets.parquet")

# push to hugginface
dataset = load_dataset("parquet", data_files="datasets.parquet")
dataset.push_to_hub("MooreFRCollections", commit_message=f"add {dictionnary_path}")

