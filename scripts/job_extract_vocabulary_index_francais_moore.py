from dotenv import load_dotenv
import base64
from typing import List
import openai
import re
import ast
from pathlib import Path
import argparse
import json
import os

load_dotenv()

openai.api_key = os.getenv("API_KEY")

def convert_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    

# Prompt spécifique pour le dictionnaire Moore-Français
def create_prompt_for_dictionary(base64_image: str) -> List[dict]:
    instruction = """Tu es un système conçu pour extraire les connaissances de documents.Le document contient un dictionnaire Moore-Français. 
    Retourne entre   custom XML-like tag such as <output>...</output>
    Pour chaque mot, il y a une explication detaillé à extraire ou plusieurs correspondance. Il faut tout extraire.
    Garde les symboles speciales telles quelles sont.
    Attention ɩ et i sont differents. 
  
    Ta tâche est d'extraire les entrées au format suivant :
    <output>[
        { "français": "mot1", "explication": "expression correspondance en moore" },
        { "rançais": "mot2", "explication": "verbe correspondances en moore, ..." }
        ...
    ]
    }</output>
     Ne fournis aucune explication supplémentaire. Conserve l'ordre des entrées tel qu'il apparaît dans le document.  
    """

    final_prompt = [{
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": f"{instruction}",
            },
            {
            "type": "image_url",
            "image_url": {
                "url":  f"data:image/jpg;base64,{base64_image}"
            },
            },
        ],
    }
    ]
    return final_prompt

def get_llm_respone(base64_image: str, model_name) -> str:
    messages =   create_prompt_for_dictionary(base64_image)
    response =   openai.ChatCompletion.create(
        model=model_name,
        messages=messages,
        max_tokens=8000,
    )
    return response["choices"][0]["message"]["content"]


def extract_output(text, tag):
    pattern = fr"<{tag}>(.*?)</{tag}>"
    matches = re.findall(pattern, text, re.DOTALL) 
    return matches[0]


def parse_page_with_gpt(image_path):
    image_base64 = convert_image_to_base64(image_path)
    llm_output =  get_llm_respone(image_base64, "gpt-4o")  
    try:
        clean_output = extract_output(llm_output, "output")
        clean_output = ast.literal_eval(clean_output)
        return clean_output

    except:
        print(image_path)
        return None



def main():
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process images and extract text.")
    parser.add_argument('folder_path', type=str, help="Path to the folder containing images")
    parser.add_argument('output_json_path', type=str, help="Path to save the result JSON")
    args = parser.parse_args()

    folder_path = args.folder_path
    output_json_path = args.output_json_path

    images = list(Path(folder_path).glob("*.jpg"))
    text_of_pages = [parse_page_with_gpt(image) for image in images]
    with open(output_json_path, 'w', encoding="utf_8") as f:
        json.dump(text_of_pages, f, indent=4, ensure_ascii=False)

    print(f"Text extracted and saved to {output_json_path}")

if __name__ == "__main__":
    main()