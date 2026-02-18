from fastapi import APIRouter
from ..schemas.language import LANGUAGES, Language
from typing import List

router = APIRouter()


@router.get("/languages", response_model=List[Language])
def get_languages():
    """回傳系統支援的語言清單（僅 zh-TW 與 en）。"""
    return [Language(**lang) for lang in LANGUAGES]
