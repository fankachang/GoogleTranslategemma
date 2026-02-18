from pydantic import BaseModel, Field
from typing import Optional, List


class GlossaryEntry(BaseModel):
    source: str
    target: str
    source_lang: Optional[str] = None
    target_lang: Optional[str] = None
    case_sensitive: bool = False


class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    source_lang: Optional[str] = None
    target_lang: Optional[str] = None
    stream: Optional[bool] = False
    glossary: Optional[List[GlossaryEntry]] = None


class TranslationResponse(BaseModel):
    translated_text: str
    detected_source_lang: Optional[str] = None
    detected: bool = False
    target_lang: Optional[str] = None
    model_name: Optional[str] = None
