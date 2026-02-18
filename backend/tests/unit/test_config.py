from backend.src.config import load_config


def test_load_config_defaults():
    cfg = load_config()
    assert isinstance(cfg, dict)
    assert "model" in cfg
    assert "device" in cfg["model"]
    assert "server" in cfg
    assert "translation" in cfg
    assert "cors" in cfg


def test_config_model_defaults():
    cfg = load_config()
    assert isinstance(cfg["model"]["name"], str)
    assert cfg["model"]["device"] in ("auto", "cpu", "cuda", "mps")


def test_config_translation_defaults():
    cfg = load_config()
    assert cfg["translation"]["timeout"] >= 1
    assert cfg["translation"]["max_new_tokens"] >= 1


def test_config_glossary_defaults():
    cfg = load_config()
    assert "glossary" in cfg
    assert isinstance(cfg["glossary"]["enabled"], bool)
    assert isinstance(cfg["glossary"]["entries"], list)
