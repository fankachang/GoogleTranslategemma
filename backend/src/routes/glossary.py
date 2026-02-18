from fastapi import APIRouter, Request
from typing import Any, Dict, List

router = APIRouter()


@router.get("/glossary", summary="取得目前術語對照表")
async def get_glossary(request: Request) -> Dict[str, Any]:
    """
    回傳目前後端載入的術語對照表設定。
    若 glossary.enabled 為 false 或無任何項目，entries 欄位為空陣列。
    """
    glossary: Dict[str, Any] = getattr(request.app.state, "glossary", {})
    enabled: bool = glossary.get("enabled", False)
    entries: List[Dict[str, Any]] = glossary.get("entries", []) if enabled else []
    return {
        "enabled": enabled,
        "entries": entries,
    }
