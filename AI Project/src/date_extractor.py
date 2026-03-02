from dateutil.parser import parse

def extract_date(text):
    """
    Extracts a due date from a text string.
    Supports:
    - MM/DD (e.g., 03/16)
    - MM/DD/YYYY
    - Natural language dates (e.g., "tomorrow", "next friday")
    - Month names (e.g., "March 16")

    Returns:
        datetime object or None
    """
    try:
        # dayfirst=False ensures MM/DD is interpreted correctly
        return parse(text, fuzzy=True, dayfirst=False)
    except:
        return None
