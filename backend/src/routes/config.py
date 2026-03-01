from fastapi import APIRouter, Request
from ..config import load_config

router = APIRouter()

_fallback_config = load_config()


@router.get("/config")
def get_config(req: Request):
    """回傳前端所需的公開設定值（無需驗證）。"""
    app_config = getattr(req.app.state, "config", _fallback_config)
    translation_cfg = app_config.get("translation", {})
    max_input_length = translation_cfg.get("max_input_length", 512)
    # 無效值（0 或負數）回退預設值
    if not isinstance(max_input_length, int) or max_input_length <= 0:
        max_input_length = 512
    return {"max_input_length": max_input_length}
