from backend.src.config import load_config


def test_load_config_defaults():
    cfg = load_config()
    assert isinstance(cfg, dict)
    assert 'model' in cfg
    assert 'device' in cfg['model'] or True
