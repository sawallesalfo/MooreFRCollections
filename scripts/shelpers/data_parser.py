import re
import pandas as pd
import urllib


def clean_text(text: str) -> str:
    """Nettoie les caractères indésirables dans une chaîne de texte."""
    text = re.sub(r"\+\s*\.", ".", text)
    text = re.sub(r"\*\s*\+\s*;", ";", text)
    text = re.sub(r"\*\s*\+", "", text)
    text = text.replace(" + ", " ").replace(" * ", " ").replace("+", " ")
    text = re.sub(r'["“”]', "", text)
    return text.strip()


def splitter(text: str) -> list[str]:
    """Divise une chaîne en segments basés sur des séparateurs spécifiques."""
    return re.split(r"[,:;.]", clean_text(text))


def flatten_nested_values(nested_values: pd.Series) -> list[str]:
    """Aplati une liste imbriquée de valeurs textuelles en une liste simple."""
    flattened = []
    for group in nested_values:
        for item in group:
            cleaned_item = re.sub(r"^\d+\s*", "", item).strip()
            if cleaned_item:
                flattened.append(cleaned_item)
    return flattened


def extract_audio_identifier(url):
    parts = url.strip("/").split("/")
    return urllib.parse.unquote(parts[-2]), int(parts[-1])
