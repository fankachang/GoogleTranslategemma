# 需求：後端整合 Ollama 模型管理

## 1. 背景與目標

目前後端使用 Hugging Face Transformers 直接於行程內載入本地 TranslateGemma 模型（4B / 12B）。  
此方式雖可行，但有以下痛點：

- 模型需手動下載並放置於 `models/` 目錄，管理繁瑣。
- 模型切換需重啟後端服務。
- 記憶體由後端行程全部持有，與其他服務共用時資源競爭明顯。

**目標**：讓後端新增 **Ollama** 作為推論後端選項；使用者可透過 `config.yaml` 切換「本地直接載入」或「透過 Ollama 管理模型」，兩種模式共用同一套 API 介面與現有功能（術語表、串流、語言清單、健康檢查等）。

---

## 2. 功能需求

### 2.1 推論後端抽象層

| 編號 | 需求 | 說明 |
|------|------|------|
| B-07 | 推論後端可切換 | 新增 `model.backend` 設定欄位，可選值為 `local`（現行）或 `ollama` |
| B-08 | 統一翻譯介面 | 所有後端需實作相同的 `translate()` 與 `stream_translate()` 方法，對路由層透明 |
| B-09 | Ollama HTTP 呼叫 | 以 HTTP 呼叫 Ollama 的 `/api/chat`（非串流）與串流端點；不引入 Ollama SDK |
| B-10 | 模型名稱對應 | Ollama 後端使用 `model.ollama_model` 欄位指定 Ollama 中的模型名稱（例如 `translategemma:4b`） |
| B-11 | 連線設定 | Ollama 後端透過 `model.ollama_base_url` 指定服務位址，預設 `http://localhost:11434` |

### 2.2 保留現有功能（不得迴歸）

| 編號 | 功能 | 說明 |
|------|------|------|
| B-01 | 翻譯 API | `POST /api/translate` 介面與行為不變 |
| B-02 | SSE 串流回應 | 兩種後端均需支援串流翻譯輸出 |
| B-03 | 模型設定檔切換 | `local` 後端仍透過 `model.name` / `model.path` 切換，行為與現行相同 |
| B-04 | 語言清單 API | `GET /api/languages` 不受後端選擇影響 |
| B-05 | 健康檢查 API | `GET /health` 需回報目前使用的後端類型與連線狀態 |
| B-GLS | 術語表（Glossary） | Glossary 功能保留；術語注入邏輯在 Prompt 組裝層，兩種後端均適用 |
| B-INP | 輸入長度限制 | `translation.max_input_length` 限制仍對兩種後端生效 |

### 2.3 Prompt 組裝

- Ollama 後端使用與現行相同的 Prompt 結構（system message + user instruction），以確保翻譯品質一致。
- 術語表注入方式維持現行做法：將術語對照附加於 system message。

### 2.4 健康檢查調整

`GET /health` 回應格式擴充：

```json
{
  "status": "ok",
  "backend": "ollama",
  "model": "translategemma:4b",
  "ollama_url": "http://localhost:11434",
  "device": null
}
```

`local` 後端維持原有 `device` 欄位；`ollama` 後端 `device` 為 `null`。

---

## 3. 設定檔規格

在現有 `config.yaml` 的 `model` 區段新增以下欄位：

```yaml
model:
  # 推論後端: "local" | "ollama"
  # local: 直接於行程載入本地模型（現行行為）
  # ollama: 透過 Ollama API 推論
  backend: "local"

  # --- Ollama 後端專用設定 ---
  # Ollama 服務位址
  ollama_base_url: "http://localhost:11434"
  # Ollama 中的模型名稱
  ollama_model: "translategemma:4b"

  # --- local 後端設定（現行，保留不動）---
  name: "4b"
  base_path: "models"
  device: "auto"
  dtype: "auto"
```

`config.example.yaml` 需同步補充上述欄位與說明注解。

---

## 4. 技術設計原則

1. **不修改路由層**：`routes/translate.py`、`routes/health.py` 等路由僅呼叫抽象介面，無需感知後端類型。
2. **最小侵入**：新增 `backend/` 模組（例如 `model_backend.py` 或 `backends/` 子套件），現有 `model.py` 的本地推論邏輯可重構為 `LocalBackend` 類別，Ollama 為 `OllamaBackend`。
3. **不引入新的大型依賴**：Ollama 呼叫使用 Python 標準函式庫 `httpx`（已在 FastAPI 生態系常用）或 `aiohttp`，避免新增重量級套件。
4. **逾時控制**：`translation.timeout` 設定同樣適用於 Ollama HTTP 請求的逾時。

---

## 5. 不在本需求範圍內

- 前端 UI 改動（介面無須顯示後端類型）。
- Ollama 自動安裝或模型自動拉取（由使用者自行管理 Ollama 服務）。
- 多模型同時運行或動態切換模型（仍為單一設定檔指定）。
- 認證 / API Key 管理（假設 Ollama 執行於本機或受信任網路）。
