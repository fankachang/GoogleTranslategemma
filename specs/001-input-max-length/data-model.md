# Data Model: 可設定的翻譯輸入字數上限

**Phase**: 1 — Design & Contracts  
**Branch**: `001-input-max-length`

---

## 設定模型（Config Layer）

### `config.yaml` — `translation` 區段

| 欄位 | 型別 | 預設值 | 有效範圍 | 說明 |
|------|------|--------|----------|------|
| `translation.max_input_length` | `int` | `512` | 1–10000 | 翻譯輸入字元上限（Unicode code points） |

**驗證規則**:
- 若值 ≤ 0 或非整數，`load_config()` 強制覆寫為 `512`
- 若欄位缺失，`setdefault` 補入 `512`

---

## 後端資料模型

### `TranslationRequest`（`backend/src/schemas/translation.py`）

| 欄位 | 型別 | 異動 | 說明 |
|------|------|------|------|
| `text` | `str` | `max_length: 5000 → 10000` | Pydantic 硬上限防止超大 payload；業務上限由 route 層動態驗證 |
| `source_lang` | `Optional[str]` | 不變 | |
| `target_lang` | `Optional[str]` | 不變 | |
| `stream` | `Optional[bool]` | 不變 | |
| `glossary` | `Optional[List[GlossaryEntry]]` | 不變 | |

### `AppConfigResponse`（新增，僅用於 `/api/config` 回應）

| 欄位 | 型別 | 說明 |
|------|------|------|
| `max_input_length` | `int` | 從 `app.state.config["translation"]["max_input_length"]` 讀取 |

> 此 schema 定義於 `backend/src/routes/config.py`（inline Pydantic model 或 TypedDict）

---

## 前端資料模型

### `AppConfig`（`frontend/AppConfig.cs`）

| 屬性 | 型別 | 異動 | 說明 |
|------|------|------|------|
| `AppTitle` | `string` | 不變 | |
| `AppLogoUrl` | `string?` | 不變 | |
| `ContentWidthPercent` | `int` | 不變 | |
| `MaxInputLength` | `int` | **新增** | 預設 `512`；`Program.cs` 啟動時從 `/api/config` 更新 |

### `TranslationInput.razor` 參數

| 參數 | 型別 | 異動 | 說明 |
|------|------|------|------|
| `IsSubmitting` | `bool` | 不變 | |
| `OnSubmit` | `EventCallback<string>` | 不變 | |
| `OnCancel` | `EventCallback` | 不變 | |
| `MaxInputLength` | `int` | **新增** | 取代硬碼 `5000`；預設值 `512` 防止父元件未傳遞時崩潰 |

---

## 驗證規則彙整

| 層級 | 驗證內容 | 失敗行為 |
|------|---------|---------|
| `config.yaml` 載入 | `max_input_length` 須為正整數 | 覆寫為 512，服務繼續 |
| Pydantic schema | `text.length ≤ 10000` | HTTP 422（標準 Pydantic 錯誤） |
| Route 業務邏輯 | `len(text) ≤ config.max_input_length` | HTTP 422，`{"detail": "輸入文字超過允許上限（{limit} 字元）"}` |
| 前端 UI | `Text.Length > MaxInputLength` | 字數顯示變紅；送出按鈕停用 |
| 前端送出前 | `Text.Length > MaxInputLength` | 中止送出（`Submit()` early return） |

---

## 狀態轉換（前端字數顯示）

```
輸入框狀態
├── [空] Length=0      → 顯示「0 / {limit}」，正常色，按鈕可用（若非 IsSubmitting）
├── [正常] 0 < L ≤ limit → 顯示「L / {limit}」，正常色，按鈕可用
└── [超限] L > limit   → 顯示「L / {limit}」，Error 色（MudBlazor Color.Error），按鈕停用
```
