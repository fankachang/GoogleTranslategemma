"""測試術語對照表替換邏輯（哨兵前置處理 + 後置還原雙階段設計）。"""
from backend.src.routes.translate import (
    _apply_glossary_preprocess,
    _apply_glossary_postprocess,
    _build_glossary_entries,
)
from backend.src.schemas.translation import GlossaryEntry


# ── 測試用術語資料 ────────────────────────────────────────────
GLOSSARY_ENTRIES = [
    {"source": "machine learning", "target": "機器學習", "source_lang": "en", "target_lang": "zh-TW", "case_sensitive": False},
    {"source": "人工智慧", "target": "Artificial Intelligence", "source_lang": "zh-TW", "target_lang": "en", "case_sensitive": False},
    {"source": "API", "target": "API", "source_lang": "en", "target_lang": "zh-TW", "case_sensitive": False},
]

GLOSSARY_CFG = {"enabled": True, "entries": GLOSSARY_ENTRIES}
DISABLED_CFG = {"enabled": False, "entries": GLOSSARY_ENTRIES}


def _full_apply(text: str, source_lang: str, target_lang: str, entries: list) -> str:
    """模擬完整術語處理流程：preprocess → （假設翻譯保留哨兵）→ postprocess。"""
    processed, sentinel_map = _apply_glossary_preprocess(text, source_lang, target_lang, entries)
    return _apply_glossary_postprocess(processed, sentinel_map)


# ── 基本替換 ────────────────────────────────────────────────
def test_glossary_basic_replacement():
    result = _full_apply("Use machine learning to train", "en", "zh-TW", GLOSSARY_ENTRIES)
    assert "機器學習" in result


def test_glossary_case_insensitive():
    result = _full_apply("Use Machine Learning to train", "en", "zh-TW", GLOSSARY_ENTRIES)
    assert "機器學習" in result


def test_glossary_reverse_direction():
    result = _full_apply("了解人工智慧的發展", "zh-TW", "en", GLOSSARY_ENTRIES)
    assert "Artificial Intelligence" in result


# ── 停用 / 方向不符 ────────────────────────────────────────
def test_glossary_disabled_no_replacement():
    entries = _build_glossary_entries(DISABLED_CFG, None)
    result = _full_apply("machine learning", "en", "zh-TW", entries)
    assert result == "machine learning"


def test_glossary_wrong_direction_no_replacement():
    # source_lang 不符（entry 要求 en，但輸入是 zh-TW）→ 不替換
    result = _full_apply("machine learning", "zh-TW", "en", GLOSSARY_ENTRIES)
    assert "machine learning" in result
    assert "機器學習" not in result


# ── 多術語 ────────────────────────────────────────────────
def test_glossary_multiple_matches():
    result = _full_apply("API and machine learning", "en", "zh-TW", GLOSSARY_ENTRIES)
    assert "API" in result
    assert "機器學習" in result


# ── 自訂術語優先於 config ──────────────────────────────────
def test_build_glossary_custom_overrides_config():
    custom = [GlossaryEntry(source="machine learning", target="ML")]
    merged = _build_glossary_entries(GLOSSARY_CFG, custom)
    result = _full_apply("Use machine learning", "en", "zh-TW", merged)
    assert "ML" in result
    assert "機器學習" not in result
