import re


def extract_segment_number(filename):
    match = re.search(r"segment_(\d+)", filename)
    return int(match.group(1)) if match else float("inf")


def get_page_segments(page_num, files):
    """
    Returns a list of files for a specific page, excluding files with specified suffixes of introduction
    """
    suffixes = ["segment_1.mp3", "segment_2.mp3", "segment_3.mp3"]

    files_page = [file for file in files if f"page_{page_num}/" in file]

    files_to_delete = [
        file for file in files_page if any(file.endswith(suffix) for suffix in suffixes)
    ]

    files_page = [file for file in files_page if file not in files_to_delete]

    return sorted(files_page, key=extract_segment_number)[3:]
