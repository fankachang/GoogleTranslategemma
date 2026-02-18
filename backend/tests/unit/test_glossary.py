"""T088: 測試術語對照表替換邏輯。"""
from backend.src.routes.translate import _apply_glossary, _apply_glossary_to_output


GLOSSARY_CFG = {
    "enabled": True,
    "entries": [
        {"source": "API", "target": "API", "source_lang": "en", "target_lang": "zh-TW", "case_sensitive": False},
        {"source": "machine learning", "target": "機器學習", "source_lang": "en", "target_lang": "zh-TW", "case_sensitive": False},
        {"source": "人工智慧", "target": "Artificial Intelligence", "source_lang": "zh-TW", "target_lang": "en", "case_sensitive": False},
    ],
}

DISABLED_CFG = {"enabled": False, "entries": GLOSSARY_CFG["entries"]}


def test_glossary_basic_replacement():
    result = _apply_glossary("Use machine learning to train", "en", "zh-TW", GLOSSARY_CFG)
    assert "機器學習" in result


def test_glossary_case_insensitive():
    result = _apply_glossary("Use Machine Learning to train", "en", "zh-TW", GLOSSARY_CFG)
    assert "機器學習" in result


def test_glossary_reverse_direction():
    result = _apply_glossary("了解人工智慧的發展", "zh-TW", "en", GLOSSARY_CFG)
    assert "Artificial Intelligence" in result


def test_glossary_disabled_no_replacement():
    result = _apply_glossary("machine learning", "en", "zh-TW", DISABLED_CFG)
    assert result == "machine learning"


def test_glossary_wrong_direction_no_replacement():
    result = _apply_glossary("machine learning", "zh-TW", "en", GLOSSARY_CFG)
    assert "machine learning" in result  # 不應替換（方向不符）


def test_glossary_multiple_matches():
    result = _apply_glossary("API and machine learning", "en", "zh-TW", GLOSSARY_CFG)
    assert "API" in result
    assert "機器學習" in result


def test_glossary_output_application():
    result = _apply_glossary_to_output("Use machine learning", "en", "zh-TW", GLOSSARY_CFG)
    assert "機器學習" in result
