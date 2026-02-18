import yaml
from pathlib import Path
from typing import Any, Dict


def load_config(path: str | None = None) -> Dict[str, Any]:
    """Load configuration from path or fallback to config.example.yaml.
    Returns a dict with sensible defaults for missing keys.
    """
    p = Path(path) if path else Path("config.yaml")
    if not p.exists():
        p = Path("config.example.yaml")
    with p.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    # Basic defaults and validation
    cfg.setdefault("model", {})
    cfg["model"].setdefault("name", "4b")
    cfg["model"].setdefault("device", "auto")
    cfg["model"].setdefault("base_path", "models")
    cfg["model"].setdefault("dtype", "auto")
    cfg.setdefault("server", {})
    cfg["server"].setdefault("host", "0.0.0.0")
    cfg["server"].setdefault("port", 8000)
    cfg.setdefault("translation", {})
    cfg["translation"].setdefault("timeout", 120)
    cfg["translation"].setdefault("max_new_tokens", 512)
    cfg.setdefault("cors", {})
    cfg["cors"].setdefault("allow_origins", ["*"])
    # glossary defaults
    cfg.setdefault("glossary", {})
    cfg["glossary"].setdefault("enabled", False)
    cfg["glossary"].setdefault("entries", [])

    return cfg
