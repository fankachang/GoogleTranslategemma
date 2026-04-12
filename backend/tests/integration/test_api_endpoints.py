import json as _json
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.config import load_config

client = TestClient(app)

# 動態讀取設定，測試與設定檔自動保持一致
_MAX_INPUT = load_config().get("translation", {}).get("max_input_length", 512)


# ──────────────────────────────
# /health
# ──────────────────────────────
def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") in ("ok", "degraded", "error")
    assert "model_name" in data
    assert "model_loaded" in data


# ──────────────────────────────
# /api/translate  (US1)
# ──────────────────────────────
def test_translate_success():
    r = client.post("/api/translate", json={"text": "Hello, world!"})
    assert r.status_code == 200
    data = r.json()
    assert "translated_text" in data
    assert isinstance(data["translated_text"], str)
    assert len(data["translated_text"]) > 0


def test_translate_empty():
    r = client.post("/api/translate", json={"text": ""})
    assert r.status_code in (400, 422)


def test_translate_whitespace_only():
    r = client.post("/api/translate", json={"text": "   \n\t  "})
    assert r.status_code in (400, 422)


def test_translate_too_long():
    r = client.post("/api/translate", json={"text": "a" * (_MAX_INPUT + 1)})
    assert r.status_code == 422


def test_translate_exactly_max_chars():
    """max_input_length 上限字元數應通過（自動讀取設定檔實際値）。"""
    r = client.post("/api/translate", json={"text": "a" * _MAX_INPUT})
    assert r.status_code == 200


def test_translate_auto_detect():
    """自動偵測語言時，detected 欄位應為 True。"""
    r = client.post("/api/translate", json={"text": "Hello"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("detected") is True


def test_translate_explicit_langs():
    """明確指定語言時，detected 欄位應為 False。"""
    r = client.post("/api/translate", json={
        "text": "Hello",
        "source_lang": "en",
        "target_lang": "zh-TW",
    })
    assert r.status_code == 200
    data = r.json()
    assert data.get("detected") is False


def test_translate_invalid_source_lang():
    r = client.post("/api/translate", json={"text": "Hello", "source_lang": "ja"})
    assert r.status_code == 422


def test_translate_same_langs():
    r = client.post("/api/translate", json={
        "text": "Hello",
        "source_lang": "en",
        "target_lang": "en",
    })
    assert r.status_code == 422


# T033a: 特殊字元
def test_translate_emoji():
    r = client.post("/api/translate", json={"text": "Hello 😀🎉"})
    assert r.status_code == 200
    assert "translated_text" in r.json()


def test_translate_symbols():
    r = client.post("/api/translate", json={"text": "Hello @#$%"})
    assert r.status_code == 200


def test_translate_newlines():
    r = client.post("/api/translate", json={"text": "Line1\nLine2\nLine3"})
    assert r.status_code == 200


# ──────────────────────────────
# /api/languages  (US2 T043)
# ──────────────────────────────
def test_get_languages():
    r = client.get("/api/languages")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    codes = {lang["code"] for lang in data}
    assert codes == {"zh-TW", "en"}, f"期望只有 zh-TW 和 en，實際: {codes}"


def test_languages_structure():
    r = client.get("/api/languages")
    for lang in r.json():
        assert "code" in lang
        assert "name" in lang
        assert "native_name" in lang


# T044: 手動選擇語言對翻譯
def test_translate_en_to_zhtw():
    r = client.post("/api/translate", json={
        "text": "Good morning",
        "source_lang": "en",
        "target_lang": "zh-TW",
    })
    assert r.status_code == 200
    data = r.json()
    assert data.get("target_lang") == "zh-TW"


def test_translate_zhtw_to_en():
    r = client.post("/api/translate", json={
        "text": "早安",
        "source_lang": "zh-TW",
        "target_lang": "en",
    })
    assert r.status_code == 200
    data = r.json()
    assert data.get("target_lang") == "en"


# ──────────────────────────────
# SSE 串流端點  (US4 T069)
# ──────────────────────────────
def test_translate_stream_returns_sse():
    """stream=true 時應回傳 text/event-stream。"""
    r = client.post("/api/translate", json={"text": "Hello", "stream": True})
    assert r.status_code == 200
    assert "text/event-stream" in r.headers.get("content-type", "")


def test_translate_stream_done_marker():
    """SSE 串流必須包含 done=true 的事件。"""
    import json as _json
    r = client.post("/api/translate", json={"text": "Hi", "stream": True})
    assert r.status_code == 200
    lines = r.text.strip().split("\n")
    data_lines = [l[6:] for l in lines if l.startswith("data: ")]
    last = _json.loads(data_lines[-1])
    assert last.get("done") is True
    assert "source_lang" in last
    assert "target_lang" in last


# ──────────────────────────────
# T017: Ollama 後端整合測試（mock backend）
# ──────────────────────────────

class _FakeOllamaBackend:
    """
    最小版 OllamaBackend stub，供路由層呼叫。
    必須有 async startup()，因為 lifespan 對非 LocalBackend 會呼叫
    asyncio.create_task(backend.startup())。
    """

    def translate(self, text, *, source_lang="zh-TW", target_lang="en"):
        return f"[翻譯] {text}"

    def translate_stream(self, text, *, source_lang="zh-TW", target_lang="en"):
        for token in ["T", "e", "s", "t"]:
            yield token

    def health_info(self):
        return {
            "status": "ok",
            "backend": "ollama",
            "model": "translategemma:4b",
            "model_name": "translategemma:4b",
            "device": None,
            "resolved_device": None,
            "model_loaded": True,
            "ollama_url": "http://localhost:11434",
        }

    async def startup(self) -> None:
        """no-op：測試環境不做真實連線。"""


@pytest.fixture()
def ollama_client():
    """
    回傳已注入 _FakeOllamaBackend 的 TestClient。
    透過 patch create_backend 確保 lifespan 從一開始就使用 fake，
    不觸發真實模型載入或 Ollama HTTP 連線（避免掛起）。
    """
    fake = _FakeOllamaBackend()
    with patch("backend.src.main.create_backend", return_value=fake):
        with TestClient(app) as c:
            yield c


def test_health_with_ollama_backend(ollama_client):
    """Ollama 後端時，/health 應回傳 backend=ollama 及 ollama_url。"""
    r = ollama_client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["backend"] == "ollama"
    assert data["ollama_url"] == "http://localhost:11434"
    assert "model_name" in data       # 向下相容欄位
    assert "model_loaded" in data
    assert data["status"] == "ok"


def test_translate_via_ollama_backend(ollama_client):
    """Ollama 後端時，/api/translate 應回傳翻譯結果及正確 model_name。"""
    r = ollama_client.post("/api/translate", json={
        "text": "Hello",
        "source_lang": "en",
        "target_lang": "zh-TW",
    })
    assert r.status_code == 200
    data = r.json()
    assert "translated_text" in data
    assert data["translated_text"] == "[翻譯] Hello"


def test_translate_stream_via_ollama_backend(ollama_client):
    """Ollama 後端時，SSE 串流應正確回傳 text/event-stream。"""
    r = ollama_client.post("/api/translate", json={
        "text": "Hello",
        "stream": True,
    })
    assert r.status_code == 200
    assert "text/event-stream" in r.headers.get("content-type", "")
    lines = r.text.strip().split("\n")
    data_lines = [l[6:] for l in lines if l.startswith("data: ")]
    last = _json.loads(data_lines[-1])
    assert last.get("done") is True


def test_translate_input_too_long_with_ollama_backend(ollama_client):
    """Ollama 後端：輸入超過 max_input_length 時應回傳 422（自動讀取設定檔上限）。"""
    r = ollama_client.post("/api/translate", json={"text": "a" * (_MAX_INPUT + 1)})
    assert r.status_code == 422


# ──────────────────────────────
# T020: 術語表 + Ollama 後端整合測試
# ──────────────────────────────

class _FakeOllamaBackendGlossary(_FakeOllamaBackend):
    """記錄收到的 text，供術語注入驗證。"""
    last_text = None

    def translate(self, text, *, source_lang="zh-TW", target_lang="en"):
        _FakeOllamaBackendGlossary.last_text = text
        return f"[翻譯] {text}"

    def translate_stream(self, text, *, source_lang="zh-TW", target_lang="en"):
        _FakeOllamaBackendGlossary.last_text = text
        yield "[翻譯] "
        yield text


@pytest.fixture()
def ollama_glossary_client():
    """注入 FakeOllamaBackendGlossary，並啟用術語表。"""
    with TestClient(app) as c:
        c.app.state.model = _FakeOllamaBackendGlossary()
        c.app.state.model_loading = False
        c.app.state.model_name = "translategemma:4b"
        c.app.state.glossary = {
            "enabled": True,
            "entries": [
                {"source": "API", "target": "應用程式介面"}
            ],
        }
        yield c


def test_glossary_injection_with_ollama_backend(ollama_glossary_client):
    """術語表啟用時，應將 API → 應用程式介面 注入（或保留原文）。"""
    r = ollama_glossary_client.post("/api/translate", json={
        "text": "API documentation",
        "source_lang": "en",
        "target_lang": "zh-TW",
    })
    assert r.status_code == 200

