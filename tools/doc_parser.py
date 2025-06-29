import re

def parse_pan(text: str) -> dict:
    """
    Extract PAN (5 letters, 4 digits, 1 letter) from text.
    Returns: {"pan": <PAN> or None}
    """
    match = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", text)
    return {"pan": match.group() if match else None}

def parse_aadhaar(text: str) -> dict:
    """
    Extract Aadhaar (formatted '1234 5678 9012') from text.
    Returns: {"aadhaar": <12-digit string> or None}
    """
    match = re.search(r"\b[0-9]{4}\s[0-9]{4}\s[0-9]{4}\b", text)
    if match:
        return {"aadhaar": match.group().replace(" ", "")}
    return {"aadhaar": None}
