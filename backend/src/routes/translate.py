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


def _apply_glossary(text: str, source_lang: str, target_lang: str, glossary_cfg: dict) -> str:
    """翻譯前：把術語對照表的原文替換為特殊標記，翻譯後再還原。
    此函式用於「翻譯前標記」步驟。實際替換在 translate 後由 _restore_glossary 執行。
    """
    if not glossary_cfg.get("enabled"):
        return text
    entries = glossary_cfg.get("entries", [])
    for entry in entries:
        if entry.get("source_lang") != source_lang or entry.get("target_lang") != target_lang:
            continue
        pattern = re.escape(entry["source"])
        flags = 0 if entry.get("case_sensitive") else re.IGNORECASE
        text = re.sub(pattern, entry["target"], text, flags=flags)
    return text


def _apply_glossary_to_output(translated: str, source_lang: str, target_lang: str, glossary_cfg: dict) -> str:
    """翻譯後：強制將輸出中出現的術語來源詞替換為指定目標詞。"""
    return _apply_glossary(translated, source_lang, target_lang, glossary_cfg)


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
    model = getattr(req.app.state, "model", None)
    app_config = getattr(req.app.state, "config", _fallback_config)
    timeout_sec = app_config.get("translation", {}).get("timeout", 120)
    model_name = getattr(req.app.state, "model_name", None)

    if request.stream:
        return StreamingResponse(
            _stream_generator(text, source, target, detected_flag, model, glossary_cfg, model_name),
            media_type="text/event-stream",
        )

    # --- 非串流 JSON 回應 ---
    try:
        loop = asyncio.new_event_loop()
        translated = _do_translate_sync(text, source, target, model, glossary_cfg, timeout_sec)
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


def _do_translate_sync(text: str, source: str, target: str, model, glossary_cfg: dict, timeout_sec: int) -> str:
    """同步執行翻譯，套用術語表。"""
    if model is not None:
        translated = model.translate(text, source_lang=source, target_lang=target)
    else:
        translated = f"[TRANSLATED ({source}→{target})]: {text}"
    return _apply_glossary_to_output(translated, source, target, glossary_cfg)


async def _stream_generator(
    text: str, source: str, target: str, detected_flag: bool,
    model, glossary_cfg: dict, model_name: str
) -> AsyncGenerator[str, None]:
    """SSE 串流生成器：每個 token 送出一個 data 事件，最後送出 done=true。"""
    try:
        if model is not None:
            for token in model.translate_stream(text, source_lang=source, target_lang=target):
                token = _apply_glossary_to_output(token, source, target, glossary_cfg)
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

