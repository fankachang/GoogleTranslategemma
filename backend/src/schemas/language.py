from pydantic import BaseModel
from typing import List, Dict


class Language(BaseModel):
    code: str
    name: str
    native_name: str


LANGUAGES: List[Dict[str, str]] = [
    {"code": "zh-TW", "name": "Chinese (Traditional)", "native_name": "繁體中文"},
    {"code": "en", "name": "English", "native_name": "English"},
]
