import pytest
from fastapi.testclient import TestClient
from backend.src.main import app

client = TestClient(app)


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
    r = client.post("/api/translate", json={"text": "a" * 5001})
    assert r.status_code == 422


def test_translate_exactly_5000_chars():
    r = client.post("/api/translate", json={"text": "a" * 5000})
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

