import re

def clean_text(text: str) -> str:
    """
    Cleans and normalizes text for ML model input.
    Steps:
    - Lowercase
    - Remove punctuation
    - Remove extra spaces
    - Keep only letters and numbers
    """

    if not isinstance(text, str):
        return ""

    # lowercase
    text = text.lower()

    # remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)

    # keep only letters, numbers and spaces
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text
