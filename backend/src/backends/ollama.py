import asyncio
import logging
from typing import Generator, Optional

import httpx

from .base import TranslationBackend

logger = logging.getLogger(__name__)


class OllamaBackend(TranslationBackend):
    """以 REST API 呼叫外部 Ollama 服務的翻譯後端。"""

    def __init__(self, ollama_base_url: str = "http://localhost:11434",
                 ollama_model: str = "translategemma:4b",
                 max_new_tokens: int = 512,
                 timeout: float = 120.0):
        self._base_url = ollama_base_url.rstrip("/")
        self._model = ollama_model
        self._max_new_tokens = max_new_tokens
        self._timeout = timeout
        # 單一 httpx.Client 實例（連線池），同時用於串流與非串流
        self._client = httpx.Client(timeout=httpx.Timeout(timeout))

    async def startup(self) -> None:
        """非同步啟動驗證：呼叫 /api/tags 確認 Ollama 服務可達，並檢查模型是否已拉取。"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._startup_sync)

    def _startup_sync(self) -> None:
        try:
            resp = self._client.get(f"{self._base_url}/api/tags", timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            models = {m.get("name", "") for m in data.get("models", [])}
            if self._model not in models:
                logger.warning(
                    "Ollama 模型未找到：backend=%s model=%s。"
                    "請確認已執行 `ollama pull %s`，或聯絡管理員。",
                    "ollama", self._model, self._model,
                )
        except Exception as exc:
            logger.error(
                "OllamaBackend 啟動驗證失敗：backend=ollama error_type=%s message=%s",
                type(exc).__name__, exc,
            )

    async def aclose(self) -> None:
        """關閉 httpx.Client，於 FastAPI lifespan 結束時呼叫。"""
        self._client.close()

    def _build_messages(self, text: str, source_lang: str, target_lang: str) -> list:
        """組裝純文字 system + user messages（不使用 TranslateGemma 專屬 chat template）。"""
        return [
            {
                "role": "system",
                "content": (
                    f"You are a translation assistant. "
                    f"Translate the following text from {source_lang} to {target_lang}. "
                    f"Output only the translated text, nothing else."
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ]

    def translate(self, text: str, source_lang: Optional[str] = None,
                  target_lang: Optional[str] = None) -> str:
        src = source_lang or "en"
        tgt = target_lang or "zh-TW"
        messages = self._build_messages(text, src, tgt)
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": self._max_new_tokens},
        }
        try:
            resp = self._client.post(
                f"{self._base_url}/api/chat",
                json=payload,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"].strip()
        except Exception as exc:
            logger.error(
                "OllamaBackend 翻譯失敗：backend=ollama error_type=%s message=%s",
                type(exc).__name__, exc,
            )
            raise

    def translate_stream(self, text: str, source_lang: Optional[str] = None,
                         target_lang: Optional[str] = None) -> Generator[str, None, None]:
        src = source_lang or "en"
        tgt = target_lang or "zh-TW"
        messages = self._build_messages(text, src, tgt)
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": True,
            "options": {"num_predict": self._max_new_tokens},
        }
        try:
            import json as _json
            with self._client.stream(
                "POST",
                f"{self._base_url}/api/chat",
                json=payload,
                timeout=self._timeout,
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = _json.loads(line)
                    except ValueError:
                        continue
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if chunk.get("done"):
                        break
        except Exception as exc:
            logger.error(
                "OllamaBackend 串流翻譯失敗：backend=ollama error_type=%s message=%s",
                type(exc).__name__, exc,
            )
            raise

    def health_info(self) -> dict:
        try:
            resp = self._client.get(
                f"{self._base_url}/api/tags",
                timeout=httpx.Timeout(5.0),
            )
            resp.raise_for_status()
            status = "ok"
        except Exception as exc:
            logger.error(
                "OllamaBackend 健康檢查失敗：backend=ollama error_type=%s message=%s",
                type(exc).__name__, exc,
            )
            status = "error"

        return {
            "status": status,
            "backend": "ollama",
            "model": self._model,
            "model_name": self._model,
            "device": None,
            "resolved_device": None,
            "model_loaded": status == "ok",
            "ollama_url": self._base_url,
        }
