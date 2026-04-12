"""OllamaBackend 單元測試。使用 unittest.mock 模擬 httpx.Client，不需要真實 Ollama 服務。"""
import json
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from backend.src.backends.ollama import OllamaBackend


# ─────────────────────────────────────────────
# 輔助工具
# ─────────────────────────────────────────────

def _make_backend(**kwargs) -> OllamaBackend:
    defaults = dict(
        ollama_base_url="http://localhost:11434",
        ollama_model="translategemma:4b",
        max_new_tokens=128,
        timeout=30.0,
    )
    defaults.update(kwargs)
    return OllamaBackend(**defaults)


# ─────────────────────────────────────────────
# T007: health_info 測試
# ─────────────────────────────────────────────

def test_health_info_ok():
    """health_info: Ollama 可達時回傳 status=ok、backend=ollama。"""
    backend = _make_backend()
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    backend._client = MagicMock()
    backend._client.get.return_value = mock_resp

    info = backend.health_info()

    assert info["status"] == "ok"
    assert info["backend"] == "ollama"
    assert info["model_loaded"] is True
    assert info["ollama_url"] == "http://localhost:11434"
    assert info["device"] is None
    assert info["resolved_device"] is None


def test_health_info_connection_error():
    """health_info: Ollama 無法連線時回傳 status=error。"""
    backend = _make_backend()
    import httpx
    backend._client = MagicMock()
    backend._client.get.side_effect = httpx.ConnectError("connection refused")

    info = backend.health_info()

    assert info["status"] == "error"
    assert info["backend"] == "ollama"
    assert info["model_loaded"] is False
    assert "ollama_url" in info


def test_health_info_timeout():
    """health_info: Ollama 健康檢查逾時時回傳 status=error。"""
    backend = _make_backend()
    import httpx
    backend._client = MagicMock()
    backend._client.get.side_effect = httpx.TimeoutException("timeout")

    info = backend.health_info()

    assert info["status"] == "error"
    assert info["backend"] == "ollama"


# ─────────────────────────────────────────────
# T007: startup 驗證測試
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_startup_model_not_found_logs_warning():
    """startup: 模型不在 /api/tags 清單時應記錄 WARNING。"""
    backend = _make_backend(ollama_model="missing-model:4b")
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"models": [{"name": "other-model:7b"}]}
    backend._client = MagicMock()
    backend._client.get.return_value = mock_resp

    with patch("backend.src.backends.ollama.logger") as mock_logger:
        await backend.startup()
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0]
        assert "ollama pull" in call_args[0]


@pytest.mark.asyncio
async def test_startup_connection_error_logs_error():
    """startup: 連線失敗時應記錄 ERROR，但不拋出例外（非硬性失敗）。"""
    backend = _make_backend()
    import httpx
    backend._client = MagicMock()
    backend._client.get.side_effect = httpx.ConnectError("refused")

    with patch("backend.src.backends.ollama.logger") as mock_logger:
        await backend.startup()  # 不應拋出例外
        mock_logger.error.assert_called_once()


# ─────────────────────────────────────────────
# T013: translate 測試（非串流）
# ─────────────────────────────────────────────

def test_translate_success():
    """translate: mock Ollama 回應，驗證回傳翻譯結果。"""
    backend = _make_backend()
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {
        "message": {"role": "assistant", "content": "你好，世界！"},
        "done": True,
    }
    backend._client = MagicMock()
    backend._client.post.return_value = mock_resp

    result = backend.translate("Hello, world!", source_lang="en", target_lang="zh-TW")

    assert result == "你好，世界！"
    backend._client.post.assert_called_once()
    call_kwargs = backend._client.post.call_args
    assert "/api/chat" in call_kwargs[0][0]
    sent_json = call_kwargs[1]["json"]
    assert sent_json["stream"] is False
    assert sent_json["model"] == "translategemma:4b"


def test_translate_uses_system_message():
    """translate: _build_messages 應產生含語言指示的 system message。"""
    backend = _make_backend()
    messages = backend._build_messages("Test", "en", "zh-TW")
    assert messages[0]["role"] == "system"
    assert "en" in messages[0]["content"]
    assert "zh-TW" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Test"


def test_translate_error_logs_and_raises():
    """translate: 例外時應記錄 ERROR 並重新拋出。"""
    backend = _make_backend()
    import httpx
    backend._client = MagicMock()
    backend._client.post.side_effect = httpx.ConnectError("refused")

    with patch("backend.src.backends.ollama.logger") as mock_logger:
        with pytest.raises(httpx.ConnectError):
            backend.translate("Hello")
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0]
        assert "backend=ollama" in call_args[0]


def test_translate_timeout_logs_and_raises():
    """translate: 逾時時應記錄 ERROR 並重新拋出。"""
    backend = _make_backend()
    import httpx
    backend._client = MagicMock()
    backend._client.post.side_effect = httpx.TimeoutException("timeout")

    with patch("backend.src.backends.ollama.logger") as mock_logger:
        with pytest.raises(httpx.TimeoutException):
            backend.translate("Hello")
        mock_logger.error.assert_called_once()


# ─────────────────────────────────────────────
# T013: translate_stream 測試
# ─────────────────────────────────────────────

def test_translate_stream_yields_tokens():
    """translate_stream: 應逐 token yield，並以最後一個 done=true chunk 結束。"""
    backend = _make_backend()

    ndjson_lines = [
        json.dumps({"message": {"content": "你"}, "done": False}),
        json.dumps({"message": {"content": "好"}, "done": False}),
        json.dumps({"message": {"content": "！"}, "done": True}),
    ]

    mock_stream_ctx = MagicMock()
    mock_stream_ctx.__enter__ = MagicMock(return_value=mock_stream_ctx)
    mock_stream_ctx.__exit__ = MagicMock(return_value=False)
    mock_stream_ctx.raise_for_status = MagicMock(return_value=None)
    mock_stream_ctx.iter_lines = MagicMock(return_value=iter(ndjson_lines))
    backend._client = MagicMock()
    backend._client.stream.return_value = mock_stream_ctx

    tokens = list(backend.translate_stream("Hello", source_lang="en", target_lang="zh-TW"))

    assert tokens == ["你", "好", "！"]


def test_translate_stream_error_logs_and_raises():
    """translate_stream: 例外時應記錄 ERROR 並重新拋出。"""
    backend = _make_backend()
    import httpx
    backend._client = MagicMock()
    backend._client.stream.side_effect = httpx.ConnectError("refused")

    with patch("backend.src.backends.ollama.logger") as mock_logger:
        with pytest.raises(httpx.ConnectError):
            list(backend.translate_stream("Hello"))
        mock_logger.error.assert_called_once()


# ─────────────────────────────────────────────
# T013: 逾時測試（透過 translate 端點路徑驗證）
# ─────────────────────────────────────────────

def test_translate_timeout_named_error():
    """timeout 應觸發 logging.error，error_type 欄位包含 TimeoutException 字樣。"""
    backend = _make_backend()
    import httpx
    backend._client = MagicMock()
    backend._client.post.side_effect = httpx.TimeoutException("timed out")

    error_logged = []
    with patch("backend.src.backends.ollama.logger") as mock_logger:
        mock_logger.error.side_effect = lambda *args, **kwargs: error_logged.append(args)
        with pytest.raises(httpx.TimeoutException):
            backend.translate("text")

    assert len(error_logged) == 1
    # 確認 error_type 欄位包含 TimeoutException 類型名稱
    assert "TimeoutException" in error_logged[0][1]


# ─────────────────────────────────────────────
# T018: 術語注入驗證
# ─────────────────────────────────────────────

def test_build_messages_with_glossary_preprocessed_text():
    """術語前置處理後的文字應被正確傳入 _build_messages。"""
    backend = _make_backend()
    # 模擬路由層術語預處理已將 "API" 替換為 "應用程式介面"
    preprocessed = "請說明 應用程式介面 的作用"
    messages = backend._build_messages(preprocessed, "zh-TW", "en")
    # user message 應含已替換的術語
    assert "應用程式介面" in messages[1]["content"]
    assert messages[0]["role"] == "system"
