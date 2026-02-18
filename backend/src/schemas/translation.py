from pydantic import BaseModel, Field
from typing import Optional


class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    source_lang: Optional[str] = None
    target_lang: Optional[str] = None
    stream: Optional[bool] = False


class TranslationResponse(BaseModel):
    translated_text: str
    detected_source_lang: Optional[str] = None
    model_name: Optional[str] = None
