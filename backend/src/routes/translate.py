import asyncio
import json
import logging
import re
from typing import AsyncGenerator

from fastapi import APIRouter, Request, HTTPException
from fastapi import status as http_status
from fastapi.responses import StreamingResponse

from ..schemas.translation import TranslationRequest, TranslationResponse
from ..language_detect import detect_language
from ..config import load_config

logger = logging.getLogger(__name__)

router = APIRouter()

SUPPORTED_LANGS = {"zh-TW", "en"}

# module-level fallback config (用於 TestClient 或 config 未掛載時)
_fallback_config = load_config()


def _apply_glossary(text: str, source_lang: str, target_lang: str, entries: list) -> str:
    """套用術語對照表：將輸出文字中匹配的原文強制替換為指定譯文。
    entries 可包含 dict（來自 config）或 GlossaryEntry pydantic 物件（來自請求）。
    source_lang / target_lang 為空時視為「匹配任意語言對」。
    """
    for entry in entries:
        if isinstance(entry, dict):
            src = entry.get("source", "")
            tgt = entry.get("target", "")
            entry_src_lang = entry.get("source_lang") or None
            entry_tgt_lang = entry.get("target_lang") or None
            cs = entry.get("case_sensitive", False)
        else:
            src = entry.source
            tgt = entry.target
            entry_src_lang = entry.source_lang or None
            entry_tgt_lang = entry.target_lang or None
            cs = entry.case_sensitive

        if entry_src_lang and entry_src_lang != source_lang:
            continue
        if entry_tgt_lang and entry_tgt_lang != target_lang:
            continue
        if not src:
            continue

        pattern = re.escape(src)
        flags = 0 if cs else re.IGNORECASE
        text = re.sub(pattern, tgt, text, flags=flags)
    return text


def _build_glossary_entries(config_glossary: dict, request_glossary) -> list:
    """合併請求端術語（優先）與 config 術語，相同原文以請求端為準。"""
    custom = list(request_glossary) if request_glossary else []
    config_enabled = config_glossary.get("enabled", False)
    config_entries = config_glossary.get("entries", []) if config_enabled else []

    if not custom:
        return config_entries
    if not config_entries:
        return custom

    custom_sources = {
        (e.source if hasattr(e, "source") else e.get("source", "")).lower()
        for e in custom
    }
    merged = custom[:]
    for cfg in config_entries:
        if cfg.get("source", "").lower() not in custom_sources:
            merged.append(cfg)
    return merged


def _resolve_langs(request: TranslationRequest, text: str):
    """解析來源/目標語言，並驗證是否在白名單內。"""
    detected_flag = False
    source = request.source_lang
    if not source:
        source = detect_language(text)
        detected_flag = True
    if source not in SUPPORTED_LANGS:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"不支援的來源語言: {source}。支援語言: {sorted(SUPPORTED_LANGS)}",
        )
    target = request.target_lang
    if not target:
        target = "en" if source == "zh-TW" else "zh-TW"
    if target not in SUPPORTED_LANGS:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"不支援的目標語言: {target}。支援語言: {sorted(SUPPORTED_LANGS)}",
        )
    if source == target:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="來源語言與目標語言不能相同",
        )
    return source, target, detected_flag


@router.post("/translate")
def translate_endpoint(request: TranslationRequest, req: Request):
    """翻譯端點：stream=false 回傳 JSON，stream=true 回傳 SSE 串流。"""
    text = request.text
    if not text or not text.strip():
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail="文字不能為空")

    source, target, detected_flag = _resolve_langs(request, text)

    glossary_cfg = getattr(req.app.state, "glossary", {"enabled": False, "entries": []})
    glossary_entries = _build_glossary_entries(glossary_cfg, request.glossary)
    model = getattr(req.app.state, "model", None)
    app_config = getattr(req.app.state, "config", _fallback_config)
    timeout_sec = app_config.get("translation", {}).get("timeout", 120)
    model_name = getattr(req.app.state, "model_name", None)

    if request.stream:
        return StreamingResponse(
            _stream_generator(text, source, target, detected_flag, model, glossary_entries, model_name),
            media_type="text/event-stream",
        )

    # --- 非串流 JSON 回應 ---
    try:
        loop = asyncio.new_event_loop()
        translated = _do_translate_sync(text, source, target, model, glossary_entries, timeout_sec)
    except TimeoutError:
        raise HTTPException(status_code=http_status.HTTP_504_GATEWAY_TIMEOUT, detail="翻譯逾時（超過120秒）")
    except Exception as e:
        logger.error("翻譯失敗: %s", e)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="翻譯失敗")

    return TranslationResponse(
        translated_text=translated,
        detected_source_lang=source,
        detected=detected_flag,
        target_lang=target,
        model_name=model_name,
    )


def _do_translate_sync(text: str, source: str, target: str, model, glossary_entries: list, timeout_sec: int) -> str:
    """同步執行翻譯，套用術語表。"""
    if model is not None:
        translated = model.translate(text, source_lang=source, target_lang=target)
    else:
        translated = f"[TRANSLATED ({source}→{target})]: {text}"
    return _apply_glossary(translated, source, target, glossary_entries)


async def _stream_generator(
    text: str, source: str, target: str, detected_flag: bool,
    model, glossary_entries: list, model_name: str
) -> AsyncGenerator[str, None]:
    """SSE 串流生成器：每個 token 送出一個 data 事件，最後送出 done=true。"""
    try:
        if model is not None:
            for token in model.translate_stream(text, source_lang=source, target_lang=target):
                token = _apply_glossary(token, source, target, glossary_entries)
                payload = json.dumps({"token": token, "done": False}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
                await asyncio.sleep(0)  # yield to event loop
        else:
            placeholder = f"[TRANSLATED ({source}→{target})]: {text}"
            for char in placeholder:
                payload = json.dumps({"token": char, "done": False}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
                await asyncio.sleep(0)

        # 最後一個 done event
        done_payload = json.dumps({
            "token": "",
            "done": True,
            "source_lang": source,
            "target_lang": target,
            "detected": detected_flag,
            "model_name": model_name,
        }, ensure_ascii=False)
        yield f"data: {done_payload}\n\n"
    except Exception as e:
        logger.error("串流翻譯失敗: %s", e)
        err_payload = json.dumps({"error": "翻譯失敗", "done": True}, ensure_ascii=False)
        yield f"data: {err_payload}\n\n"

