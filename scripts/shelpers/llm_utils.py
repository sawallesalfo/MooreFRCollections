import re
import base64
import json
from loguru import logger

from .s3_utils import download_file_from_s3, upload_file_to_s3
from .data_parser import splitter, flatten_nested_values
from .path_collectors import get_page_segments


from rapidfuzz import fuzz, process


def remove_similar_elements(input_list, elements_to_remove, threshold=85):

    result = []
    for item in input_list:
        matches = process.extract(item, elements_to_remove, scorer=fuzz.ratio, limit=1)
        if not matches or matches[0][1] < threshold:
            result.append(item)
    return result


def audio_to_base64(audio_file_path):

    with open(audio_file_path, "rb") as mp3_file:
        binary_content = mp3_file.read()
        base64_encoded = base64.b64encode(binary_content)
        return base64_encoded.decode("utf-8")


def save_results(data, file_path):
    """Saves the results to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def extract_xml_tag(content, tag):
    pattern = rf"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else None


def string_to_list(input_text, preserve_delimiter=False):
    if preserve_delimiter:
        parts = input_text.split(",")
        return [
            part.strip() + "," if idx < len(parts) - 1 else part.strip()
            for idx, part in enumerate(parts)
        ]
    else:
        # Split and remove the delimiter
        return [part.strip() for part in input_text.split(",") if part.strip()]


def chat_with_audio(
    client, query, input_audio_base64, model, system_prompt, audio_format="mp3"
):
    """
    Sends a chat request to the OpenAI API with a combination of text and audio input.

    Parameters:
    - client: The OpenAI client instance.
    - model: The name of the OpenAI model to use.
    - system_prompt: A string representing the system's instructions or prompt.
    - query: The user's text query.
    - input_audio_base64: The base64-encoded audio input.
    - audio_format: The format of the input audio (default: "mp3").

    Returns:
    - The response from the OpenAI API.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": str(query)},
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": input_audio_base64,
                            "format": audio_format,
                        },
                    },
                ],
            },
        ],
        modalities=["text"],
        response_format={"type": "text"},
    )
    return response


def process_single_page(
    page_num,
    tmp,
    files,
    openai_client,
    s3_client,
    BUCKET_NAME,
    MODEL_NAME,
    SYSTEM_PROMPT,
    BATCH_SIZE=20,
):
    """
    Process a single page for audio transcription and grading.

    Parameters:
    - page_num: The page number to process.
    - tmp: The dataframe containing the page data.
    - files: List of files available for processing.
    - openai_client: The OpenAI client for interacting with the API.
    - S3_client:
    - BUCKET_NAME: The name of the S3 bucket.
    - MODEL_NAME: The model name for the OpenAI API.
    - SYSTEM_PROMPT: The system prompt for the OpenAI API.
    - BATCH_SIZE: Number of results to save per batch.

    Returns:
    - results: List of dictionaries with audio transcription and grades.
    """
    results = []
    tmp = tmp[tmp.page == page_num].reset_index(drop=True)
    possible_values = tmp["moore_verse_text"].apply(splitter)
    inputs = flatten_nested_values(possible_values)
    page_files = get_page_segments(page_num, files)

    verses = inputs.copy()
    _transcription = ""

    for idx, file in list(enumerate(page_files, 1))[:2]:
        download_file_from_s3(s3_client, BUCKET_NAME, file, file)
        audio_base64 = audio_to_base64(file)
        print(f"Processing audio {file}")

        # Use the first 10 verses as input.
        elligible_candidates = verses[:10]

        response = chat_with_audio(
            openai_client, elligible_candidates, audio_base64, MODEL_NAME, SYSTEM_PROMPT
        )
        result = response.choices[0].message.content

        transcription = extract_xml_tag(result, "output")
        grade = extract_xml_tag(result, "grade")
        logger.info(f"model result: {result}")

        results.append(
            {
                "audio_path": file,
                "grade": grade,
                "transcription": transcription,
            }
        )
        _transcription = _transcription + "," + transcription
        if idx % 3 == 0:
            verses = remove_similar_elements(
                verses, string_to_list(_transcription), threshold=95
            )
            _transcription = ""

        # Save results every BATCH_SIZE files.
        if idx % BATCH_SIZE == 0:
            save_results(results, f"{file}.json")
            upload_file_to_s3(
                s3_client,
                f"{file}.json",
                BUCKET_NAME,
                f"model_transcription/{file}.json",
            )
            results = []  # Reset results after saving

    # Save remaining results after processing all files.
    if results:
        prefix = file.split("/")[1]
        save_results(results, f"{prefix}_{page_num}_final_batch.json")
        upload_file_to_s3(
            s3_client,
            f"{prefix}_{page_num}_final_batch.json",
            BUCKET_NAME,
            f"model_transcription/aggregated/{prefix}/{page_num}_final_batch.json",
        )

    return results
