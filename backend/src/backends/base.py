from abc import ABC, abstractmethod
from typing import Generator, Optional


class TranslationBackend(ABC):
    """翻譯後端抽象介面。所有具體後端均須實作此介面。"""

    @abstractmethod
    def translate(self, text: str, source_lang: Optional[str] = None,
                  target_lang: Optional[str] = None) -> str:
        """執行單次翻譯，回傳翻譯結果字串。"""

    @abstractmethod
    def translate_stream(self, text: str, source_lang: Optional[str] = None,
                         target_lang: Optional[str] = None) -> Generator[str, None, None]:
        """逐 token 串流翻譯，yield 每個 token 字串。"""

    @abstractmethod
    def health_info(self) -> dict:
        """回傳健康狀態 dict，供 GET /health 路由使用。"""
