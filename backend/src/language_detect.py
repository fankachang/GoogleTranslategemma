import re
from typing import Literal


def detect_language(text: str, cjk_threshold: float = 0.2) -> Literal['zh-TW', 'en']:
    """以 CJK 字元在有效字元（CJK + 英文字母）中的佔比判斷語系。

    cjk_threshold: CJK 佔比達到此值（含）即判為 zh-TW，預設 0.2（20%）。
    空字串或無有效字元時預設回傳 'en'。
    """
    if not text or not text.strip():
        return 'en'

    cjk_count = len(re.findall(r'[\u4e00-\u9fff]', text))
    latin_count = len(re.findall(r'[A-Za-z]', text))
    total = cjk_count + latin_count

    if total == 0:
        return 'en'

    if cjk_count / total >= cjk_threshold:
        return 'zh-TW'

    return 'en'
