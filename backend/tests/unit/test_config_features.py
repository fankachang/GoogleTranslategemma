"""測試 load_config() 的 features 區塊預設值與型別驗證。"""
import tempfile
import os
from backend.src.config import load_config


def _write_config(content: str) -> str:
    """寫入臨時 config 檔案，回傳路徑。"""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8")
    f.write(content)
    f.flush()
    f.close()
    return f.name


def test_features_default_when_missing():
    """config.yaml 中完全未定義 features 時，language_selector 應預設 False。"""
    path = _write_config("model:\n  backend: local\n")
    try:
        cfg = load_config(path)
        assert "features" in cfg
        assert cfg["features"]["language_selector"] is False
    finally:
        os.unlink(path)


def test_features_language_selector_true():
    """config.yaml 中 features.language_selector: true 時，應回傳 True。"""
    path = _write_config("features:\n  language_selector: true\n")
    try:
        cfg = load_config(path)
        assert cfg["features"]["language_selector"] is True
    finally:
        os.unlink(path)


def test_features_language_selector_false():
    """config.yaml 中 features.language_selector: false 時，應回傳 False。"""
    path = _write_config("features:\n  language_selector: false\n")
    try:
        cfg = load_config(path)
        assert cfg["features"]["language_selector"] is False
    finally:
        os.unlink(path)


def test_features_block_missing_key():
    """features 區塊存在但缺少 language_selector 鍵時，應預設 False。"""
    path = _write_config("features:\n  other_flag: true\n")
    try:
        cfg = load_config(path)
        assert cfg["features"]["language_selector"] is False
    finally:
        os.unlink(path)
