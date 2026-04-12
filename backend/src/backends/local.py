from typing import Generator, Optional

from .base import TranslationBackend
from ..model import TranslateGemmaModel


class LocalBackend(TranslationBackend):
    """行程內直接載入本地模型的翻譯後端。封裝現有 TranslateGemmaModel，架構不變。"""

    def __init__(self, model_name: str = "4b", device: str = "auto",
                 base_path: str = "models", dtype: str = "auto",
                 max_new_tokens: int = 512, model_path: str = ""):
        self._model = TranslateGemmaModel(
            model_name=model_name,
            device=device,
            base_path=base_path,
            dtype=dtype,
            max_new_tokens=max_new_tokens,
            model_path=model_path,
        )
        self._model_name = model_name
        self._device = device

    def load(self) -> None:
        """載入模型（委派至 TranslateGemmaModel.load）。"""
        self._model.load()

    def translate(self, text: str, source_lang: Optional[str] = None,
                  target_lang: Optional[str] = None) -> str:
        return self._model.translate(text, source_lang=source_lang, target_lang=target_lang)

    def translate_stream(self, text: str, source_lang: Optional[str] = None,
                         target_lang: Optional[str] = None) -> Generator[str, None, None]:
        return self._model.translate_stream(text, source_lang=source_lang, target_lang=target_lang)

    def health_info(self) -> dict:
        loaded = self._model.model is not None
        name_map = {"4b": "Translategemma-4b-it", "12b": "Translategemma-12b-it"}
        display_name = self._model.model_path or name_map.get(self._model_name, self._model_name)
        status = "ok" if loaded else "degraded"
        return {
            "status": status,
            "backend": "local",
            "model": display_name,
            "model_name": self._model_name,
            "device": self._device,
            "resolved_device": self._model._resolved_device,
            "model_loaded": loaded,
            "ollama_url": None,
        }
