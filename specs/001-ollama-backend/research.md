# 研究報告：後端整合 Ollama 模型管理

**功能分支**：`001-ollama-backend`  
**日期**：2026-04-12  
**狀態**：完成

---

## 研究項目 1：Ollama REST API 介面

### 決策
使用 Ollama 的 `/api/chat` 端點（支援串流與非串流模式）。

### 說明

Ollama 提供標準 HTTP REST API：

**非串流翻譯請求**：
```
POST http://localhost:11434/api/chat
Content-Type: application/json

{
  "model": "translategemma:4b",
  "messages": [
    {"role": "system", "content": "...術語注入 system message..."},
    {"role": "user",   "content": "Translate the following..."}
  ],
  "stream": false
}
```
回應：`{"message": {"role": "assistant", "content": "翻譯結果"}, "done": true}`

**串流模式**：設定 `"stream": true`，回應為 NDJSON（換行分隔的 JSON），每行格式：
```json
{"message": {"role": "assistant", "content": "token"}, "done": false}
```
最後一行 `"done": true` 代表串流結束。

**健康/連線確認**：`GET http://localhost:11434/api/tags` 用於檢查 Ollama 服務是否可達，回傳已拉取的模型清單。

### 替代方案考量
- 使用 `ollama` Python 套件：排除，符合 Constitution Principle III（YAGNI）；httpx 已足夠，不增加額外依賴。
- 使用 `/api/generate`（非 chat 格式）：排除，現有 Prompt 使用 messages 格式（system + user），`/api/chat` 可直接沿用，不需轉換。

---

## 研究項目 2：HTTP 客戶端選擇

### 決策
使用 `httpx`（`httpx.AsyncClient`）進行 HTTP 呼叫。

### 說明
- `httpx` 已廣泛用於 FastAPI 測試（`httpx.AsyncClient` 是 `TestClient` 的底層），大概率已在測試環境中安裝。
- 支援 async/await，與 FastAPI 的 async 路由原生整合。
- 支援 streaming response（`stream()`），適合接收 NDJSON 串流並逐行轉換為 SSE。
- 不需額外安裝 SDK，符合 Constitution Principle III。

### 替代方案考量
- `aiohttp`：功能相當，但 `httpx` 與 FastAPI 生態系更一致，已在 requirements.txt 的測試鏈中出現。
- `requests`（同步）：無法與 async FastAPI 路由直接搭配，需 `run_in_executor` 包裝，不選用。

**需補充 requirements.txt**：`httpx` 若未列入需新增。

---

## 研究項目 3：後端抽象層設計（最小侵入）

### 決策
新增 `backend/src/backends/` 子套件，定義抽象基底類別 `TranslationBackend`，現有 `TranslateGemmaModel` 重構為 `LocalBackend`，新增 `OllamaBackend`。`main.py` 的 lifespan 依 `model.backend` 設定值選擇具體實作。

### 說明

現有架構：
```
model.py            → TranslateGemmaModel（含 load, translate, translate_stream）
routes/translate.py → 透過 app.state.model 呼叫 translate / translate_stream
routes/health.py    → 透過 app.state.model 讀取 model.model, _resolved_device
```

新增後結構（最小侵入）：
```
backends/
├── __init__.py         → 匯出 create_backend(config) 工廠函式
├── base.py             → TranslationBackend ABC（抽象基底類別）
├── local.py            → LocalBackend（現有 TranslateGemmaModel 邏輯移入）
└── ollama.py           → OllamaBackend（httpx 呼叫 Ollama REST API）
```

- `routes/translate.py` 只需確認 `app.state.model` 實作 `translate()` 與 `translate_stream()`，無需任何修改。
- `routes/health.py` 需小幅調整：增加 `backend` 欄位；`OllamaBackend` 提供 `health_info()` 方法回傳連線狀態。
- `main.py` 的 lifespan 改為呼叫 `create_backend(config)` 工廠函式，依設定選擇實作。

### Prompt 組裝
現有 `_build_messages()` 在 `TranslateGemmaModel` 內，使用 TranslateGemma 的 chat template 特殊格式（type / source_lang_code / target_lang_code）。Ollama 後端使用一般 OpenAI-compatible messages 格式（system + user 純文字），因此 `OllamaBackend` 需自行組裝 Prompt，例如：

```
system: "You are a translation model. Translate from {source_lang} to {target_lang}. [術語注入]"
user: "Translate:\n{text}"
```

術語注入邏輯（`_apply_glossary_preprocess`）已在 `routes/translate.py` 層執行，直接修改輸入文字，與後端類型無關，**無需修改**。

### 替代方案考量
- 直接在 `model.py` 加 if/else：排除，會破壞現有 local 架構可讀性，違反 Constitution Principle III。
- 修改路由層感知後端類型：排除，增加耦合，違反 FR-008。

---

## 研究項目 4：健康檢查擴充策略

### 決策
`health.py` 路由新增 `backend` 欄位；後端物件提供統一的 `health_info()` dict 方法，保留現有欄位並補充新欄位。

### 說明

現有 health 回應欄位：`status, model_name, device, resolved_device, model_loaded`

目標回應（`ollama` 後端）：
```json
{
  "status": "ok" | "error" | "degraded",
  "backend": "ollama",
  "model": "translategemma:4b",
  "ollama_url": "http://localhost:11434",
  "device": null,
  "resolved_device": null,
  "model_loaded": true
}
```

目標回應（`local` 後端，向下相容）：
```json
{
  "status": "ok",
  "backend": "local",
  "model": "Translategemma-4b-it",
  "device": "auto",
  "resolved_device": "mps",
  "model_loaded": true
}
```

`OllamaBackend` 的連線檢查透過 `GET /api/tags` 進行，若連線失敗則 `status: error`；成功則 `status: ok`（無法確認 model 已載入，以 `model_loaded: true` 視為樂觀假設）。

---

## 研究項目 5：設定檔向下相容性

### 決策
`config.py` 的 `load_config()` 新增 `backend`、`ollama_base_url`、`ollama_model` 三個預設值，現有欄位完全保留。

### 說明

新增的 `setdefault` 呼叫：
```python
cfg["model"].setdefault("backend", "local")
cfg["model"].setdefault("ollama_base_url", "http://localhost:11434")
cfg["model"].setdefault("ollama_model", "translategemma:4b")
```

不存在 `backend` 欄位的舊設定檔，預設值 `local` 確保行為完全與現行相同。

---

## 研究項目 6：測試策略

### 決策
- 現有單元測試（`test_model.py`）確認 `LocalBackend` 行為不迴歸。
- 新增 `test_ollama_backend.py`：使用 `unittest.mock` 或 `respx`（httpx 的 mock 庫）模擬 Ollama HTTP 回應，驗證 `OllamaBackend` 的翻譯、串流、健康檢查、逾時行為。
- 整合測試 `test_api_endpoints.py` 擴充：以 mock Ollama 後端驗證 `backend: ollama` 設定下的所有端點回應格式。

### 新增依賴評估
- `respx`（httpx mock）：可選。若僅用 `unittest.mock.patch`，無需新增依賴；`respx` 更易讀但屬額外套件。決策：優先使用 `unittest.mock.AsyncMock`，如複雜度提高再評估 `respx`。

---

## 所有 NEEDS CLARIFICATION 已解決

| 項目 | 確認結果 |
|------|---------|
| Ollama API 端點 | `/api/chat`（串流）、`/api/tags`（健康檢查） |
| HTTP 客戶端 | `httpx.AsyncClient` |
| Prompt 格式 | Ollama 後端使用純文字 system + user message，非 TranslateGemma chat template |
| 術語注入 | 在路由層（preprocess）已完成，兩種後端均適用，無需修改 |
| 設定檔相容 | `model.backend` 新欄位，預設 `local`，向下相容 |
| 測試方式 | `unittest.mock.AsyncMock` mock httpx |
