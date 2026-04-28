"""整合測試：GET /api/config 應回傳含 features.language_selector 的 JSON 結構。"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.src.main import app

client = TestClient(app)


def test_api_config_contains_features():
    """GET /api/config 應回傳含 features 欄位的回應。"""
    r = client.get("/api/config")
    assert r.status_code == 200
    data = r.json()
    assert "features" in data, "回應應包含 features 欄位"
    assert "language_selector" in data["features"], "features 應包含 language_selector 欄位"
    assert isinstance(data["features"]["language_selector"], bool), "language_selector 應為 bool"


def test_api_config_language_selector_false_by_default():
    """預設設定下 language_selector 應為 False。"""
    r = client.get("/api/config")
    assert r.status_code == 200
    data = r.json()
    # 預設 config 中 language_selector 為 false
    assert data["features"]["language_selector"] is False


def test_api_config_language_selector_true_when_enabled():
    """當設定中 features.language_selector = True 時，API 應回傳 true。"""
    mock_config = {
        "translation": {"max_input_length": 512},
        "features": {"language_selector": True},
    }
    with patch.object(app.state, "config", mock_config, create=True):
        r = client.get("/api/config")
    assert r.status_code == 200
    data = r.json()
    assert data["features"]["language_selector"] is True


def test_api_config_language_selector_non_bool_fallback():
    """features.language_selector 為非 bool 值時，API 應回退 False。"""
    mock_config = {
        "translation": {"max_input_length": 512},
        "features": {"language_selector": "yes"},  # 非 bool
    }
    with patch.object(app.state, "config", mock_config, create=True):
        r = client.get("/api/config")
    assert r.status_code == 200
    data = r.json()
    assert data["features"]["language_selector"] is False


def test_api_config_max_input_length_still_present():
    """確認既有 max_input_length 欄位仍回傳，向下相容。"""
    r = client.get("/api/config")
    assert r.status_code == 200
    data = r.json()
    assert "max_input_length" in data
    assert isinstance(data["max_input_length"], int)
    assert data["max_input_length"] > 0
