from .base import TranslationBackend
from .local import LocalBackend
from .ollama import OllamaBackend

__all__ = ["TranslationBackend", "LocalBackend", "OllamaBackend", "create_backend"]


def create_backend(config: dict) -> TranslationBackend:
    """工廠函式：依 config["model"]["backend"] 建立對應的翻譯後端實例。"""
    model_cfg = config.get("model", {})
    translation_cfg = config.get("translation", {})
    backend_type = model_cfg.get("backend", "local")

    if backend_type == "ollama":
        return OllamaBackend(
            ollama_base_url=model_cfg.get("ollama_base_url", "http://localhost:11434"),
            ollama_model=model_cfg.get("ollama_model", "translategemma:4b"),
            max_new_tokens=translation_cfg.get("max_new_tokens", 512),
            timeout=float(translation_cfg.get("timeout", 120)),
        )

    return LocalBackend(
        model_name=model_cfg.get("name", "4b"),
        device=model_cfg.get("device", "auto"),
        base_path=model_cfg.get("base_path", "models"),
        dtype=model_cfg.get("dtype", "auto"),
        max_new_tokens=translation_cfg.get("max_new_tokens", 512),
        model_path=model_cfg.get("path", ""),
    )
