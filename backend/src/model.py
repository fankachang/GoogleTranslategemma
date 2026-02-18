import logging
from pathlib import Path
from typing import Optional, Generator

logger = logging.getLogger(__name__)

# 支援的語言名稱對照（供 chat template 使用）
LANG_NAMES = {
    "zh-TW": "Traditional Chinese",
    "en": "English",
}


class TranslateGemmaModel:
    def __init__(self, model_name: str = "4b", device: str = "auto", base_path: str = "models",
                 dtype: str = "auto", max_new_tokens: int = 512):
        self.model_name = model_name
        self.device = device
        self.base_path = base_path
        self.dtype = dtype
        self.max_new_tokens = max_new_tokens
        self.model = None
        self.tokenizer = None
        self._resolved_device = "cpu"

    def _resolve_device(self) -> str:
        if self.device != "auto":
            return self.device
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        return "cpu"

    def _resolve_dtype(self, device: str):
        try:
            import torch
            if self.dtype == "auto":
                return torch.bfloat16 if device in ("cuda", "mps") else torch.float32
            mapping = {
                "bfloat16": torch.bfloat16,
                "float16": torch.float16,
                "float32": torch.float32,
            }
            return mapping.get(self.dtype, torch.float32)
        except ImportError:
            return None

    def _get_model_path(self) -> str:
        """根據 model_name (4b/12b) 對應本地模型目錄."""
        name_map = {
            "4b": "Translategemma-4b-it",
            "12b": "Translategemma-12b-it",
        }
        folder = name_map.get(self.model_name, self.model_name)
        local_path = Path(self.base_path) / folder
        if local_path.exists():
            return str(local_path)
        # fallback: 當作 HuggingFace model id
        return self.model_name

    def load(self) -> None:
        """載入 tokenizer/model，失敗時保持 None（graceful fallback）."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch

            model_path = self._get_model_path()
            self._resolved_device = self._resolve_device()
            torch_dtype = self._resolve_dtype(self._resolved_device)

            logger.info("載入模型 %s 到 %s (dtype=%s)", model_path, self._resolved_device, torch_dtype)
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch_dtype,
                device_map=self._resolved_device,
            )
            self.model.eval()
            logger.info("模型載入完成")
        except Exception as e:
            logger.warning("模型載入失敗: %s，使用 placeholder 模式", e)
            self.tokenizer = None
            self.model = None

    def _build_prompt(self, text: str, source_lang: str, target_lang: str) -> str:
        src_name = LANG_NAMES.get(source_lang, source_lang)
        tgt_name = LANG_NAMES.get(target_lang, target_lang)
        return (
            f"Translate the following text from {src_name} to {tgt_name}.\n"
            f"Text: {text}\n"
            f"Translation:"
        )

    def translate(self, text: str, source_lang: Optional[str] = None, target_lang: Optional[str] = None) -> str:
        """執行翻譯。模型未載入時回傳 placeholder."""
        src = source_lang or "en"
        tgt = target_lang or "zh-TW"

        if not self.model or not self.tokenizer:
            return f"[TRANSLATED ({src}→{tgt})]: {text}"

        prompt = self._build_prompt(text, src, tgt)
        try:
            import torch
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self._resolved_device)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_new_tokens,
                    do_sample=False,
                )
            # 只取生成部分（去掉 prompt tokens）
            generated = outputs[0][inputs["input_ids"].shape[1]:]
            return self.tokenizer.decode(generated, skip_special_tokens=True).strip()
        except Exception as e:
            logger.error("翻譯推論失敗: %s", e)
            raise

    def translate_stream(self, text: str, source_lang: Optional[str] = None,
                         target_lang: Optional[str] = None) -> Generator[str, None, None]:
        """逐 token 串流生成，yield 每個 decoded token string."""
        src = source_lang or "en"
        tgt = target_lang or "zh-TW"

        if not self.model or not self.tokenizer:
            # placeholder 串流
            placeholder = f"[TRANSLATED ({src}→{tgt})]: {text}"
            for char in placeholder:
                yield char
            return

        prompt = self._build_prompt(text, src, tgt)
        try:
            import torch
            from transformers import TextIteratorStreamer
            from threading import Thread

            inputs = self.tokenizer(prompt, return_tensors="pt").to(self._resolved_device)
            streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
            gen_kwargs = dict(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                streamer=streamer,
            )
            thread = Thread(target=self.model.generate, kwargs=gen_kwargs)
            thread.start()
            for token in streamer:
                yield token
            thread.join()
        except Exception as e:
            logger.error("串流翻譯失敗: %s", e)
            raise
