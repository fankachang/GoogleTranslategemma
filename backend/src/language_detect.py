import re
from typing import Literal


def detect_language(text: str) -> Literal['zh-TW', 'en']:
    """Detect language simply: if contains CJK unified ideographs -> zh-TW, else if contains ascii letters -> en.
    Defaults to 'en' for empty/unknown.
    """
    if not text or not text.strip():
        return 'en'

    # If contains Chinese characters, assume Traditional Chinese (zh-TW)
    if re.search(r'[\u4e00-\u9fff]', text):
        return 'zh-TW'

    # If contains Latin letters, assume English
    if re.search(r'[A-Za-z]', text):
        return 'en'

    return 'en'
