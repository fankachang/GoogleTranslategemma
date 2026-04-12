# 資料模型：後端整合 Ollama 模型管理

**功能分支**：`001-ollama-backend`  
**日期**：2026-04-12

---

## 實體與類別關係

```
TranslationBackend (ABC)
├── LocalBackend          ← 現有 TranslateGemmaModel 邏輯移入
└── OllamaBackend         ← 新增

create_backend(config) → TranslationBackend  ← 工廠函式
```

---

## TranslationBackend（抽象基底類別）

**檔案**：`backend/src/backends/base.py`

| 方法 | 簽名 | 說明 |
|------|------|------|
| `translate` | `(text, source_lang, target_lang) → str` | 同步完整翻譯 |
| `translate_stream` | `(text, source_lang, target_lang) → Generator[str, None, None]` | 逐 token 串流翻譯 |
| `health_info` | `() → dict` | 健康狀態 dict，供 health 路由使用 |

---

## LocalBackend

**檔案**：`backend/src/backends/local.py`  
**來源**：現有 `TranslateGemmaModel`（邏輯平移，無破壞性修改）

| 屬性 | 型別 | 說明 |
|------|------|------|
| `model_name` | `str` | 模型簡稱（`4b` / `12b`） |
| `device` | `str` | 推論裝置設定（`auto`/`cuda`/`mps`/`cpu`） |
| `base_path` | `str` | 模型根目錄 |
| `dtype` | `str` | 資料型別設定 |
| `max_new_tokens` | `int` | 最大生成 token 數 |
| `model_path` | `str` | 覆蓋目錄名稱（可為空字串） |
| `model` | `Optional[Any]` | HuggingFace model 物件 |
| `tokenizer` | `Optional[Any]` | HuggingFace tokenizer 物件 |
| `_resolved_device` | `str` | 實際使用的裝置 |

| 方法 | 說明 |
|------|------|
| `load()` | 載入 tokenizer + model；失敗時 graceful fallback |
| `translate(...)` | 使用 chat template 推論，回傳翻譯結果 |
| `translate_stream(...)` | 使用 TextIteratorStreamer 逐 token yield |
| `health_info()` | 回傳 `backend: local`、裝置資訊、載入狀態 |

---

## OllamaBackend

**檔案**：`backend/src/backends/ollama.py`

| 屬性 | 型別 | 說明 |
|------|------|------|
| `ollama_base_url` | `str` | Ollama 服務位址，預設 `http://localhost:11434` |
| `ollama_model` | `str` | Ollama 中的模型名稱，預設 `translategemma:4b` |
| `max_new_tokens` | `int` | 對應 `num_predict` 傳入 Ollama |
| `timeout` | `float` | HTTP 請求逾時秒數 |

| 方法 | 說明 |
|------|------|
| `translate(...)` | 呼叫 `POST /api/chat`（`stream: false`），解析回應 |
| `translate_stream(...)` | 呼叫 `POST /api/chat`（`stream: true`），逐行解析 NDJSON，yield token |
| `health_info()` | 呼叫 `GET /api/tags` 確認連線，回傳 `backend: ollama`、連線狀態 |
| `_build_messages(text, source_lang, target_lang)` | 組裝 system + user messages |

---

## 工廠函式

**檔案**：`backend/src/backends/__init__.py`

```python
def create_backend(config: dict) -> TranslationBackend:
    backend_type = config.get("model", {}).get("backend", "local")
    if backend_type == "ollama":
        return OllamaBackend(...)
    return LocalBackend(...)
```

---

## 設定欄位擴充（`config.py`）

現有 `load_config()` 新增三個 setdefault：

| 欄位 | 路徑 | 預設值 | 說明 |
|------|------|--------|------|
| `backend` | `model.backend` | `"local"` | 後端類型選擇 |
| `ollama_base_url` | `model.ollama_base_url` | `"http://localhost:11434"` | Ollama 服務位址 |
| `ollama_model` | `model.ollama_model` | `"translategemma:4b"` | Ollama 模型名稱 |

---

## health 回應格式

| 欄位 | local 後端 | ollama 後端 |
|------|-----------|------------|
| `status` | `ok` / `loading` / `degraded` / `error` | `ok` / `error` |
| `backend` | `"local"` | `"ollama"` |
| `model` | 模型路徑名稱 | `ollama_model` 值 |
| `ollama_url` | 不含 | Ollama 服務位址 |
| `device` | 設定值 | `null` |
| `resolved_device` | 實際裝置 | `null` |
| `model_loaded` | `true` / `false` | `true`（連線成功後樂觀假設） |

---

## 狀態轉換

### LocalBackend 啟動流程
```
建立 LocalBackend → load()（背景執行）→ model_loading=True → 載入完成 → model_loading=False
```

### OllamaBackend 啟動流程
```
建立 OllamaBackend → 無需載入，立即就緒 → health_info() 在請求時確認連線
```
