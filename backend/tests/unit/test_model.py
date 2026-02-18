"""T075: 測試 TranslateGemmaModel 模型載入、推論、裝置選擇邏輯（不需要真實 GPU）。"""
from backend.src.model import TranslateGemmaModel


def test_model_init_defaults():
    m = TranslateGemmaModel()
    assert m.model_name == "4b"
    assert m.device == "auto"
    assert m.model is None
    assert m.tokenizer is None


def test_model_translate_placeholder():
    """未載入模型時應回傳 placeholder 翻譯。"""
    m = TranslateGemmaModel()
    result = m.translate("Hello", source_lang="en", target_lang="zh-TW")
    assert "Hello" in result
    assert isinstance(result, str)


def test_model_translate_stream_placeholder():
    """未載入模型時串流應 yield placeholder 字元。"""
    m = TranslateGemmaModel()
    tokens = list(m.translate_stream("Hi", source_lang="en", target_lang="zh-TW"))
    combined = "".join(tokens)
    assert "Hi" in combined
    assert len(tokens) > 0


def test_model_resolve_device_cpu():
    m = TranslateGemmaModel(device="cpu")
    assert m._resolve_device() == "cpu"


def test_model_resolve_device_auto_returns_string():
    """auto 裝置應回傳 cpu/cuda/mps 其中之一（取決於環境）。"""
    m = TranslateGemmaModel(device="auto")
    result = m._resolve_device()
    assert result in ("cpu", "cuda", "mps")


def test_model_build_prompt():
    m = TranslateGemmaModel()
    prompt = m._build_prompt("Hello", "en", "zh-TW")
    assert "English" in prompt
    assert "Traditional Chinese" in prompt
    assert "Hello" in prompt
