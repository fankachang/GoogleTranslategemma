# Feature Specification: 後端整合 Ollama 模型管理

**Feature Branch**: `001-ollama-backend`  
**Created**: 2026-04-12  
**Status**: Draft  
**Input**: User description: "後端整合 Ollama 模型管理，保留術語表等現有功能"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 管理員選擇 Ollama 作為推論後端 (Priority: P1)

管理員在保留現有 local 後端架構不變的情況下，可透過 `config.yaml` 選擇改用 Ollama REST API 進行推論。只需將 `model.backend` 設為 `ollama` 並填入 Ollama 服務位址與模型名稱，重啟後端後即可使用，無需任何程式碼改動；隨時可改回 `local` 恢復原本行為。

**Why this priority**: 這是本功能的核心目標。兩種後端選項均可正常運作，且可自由切換，即代表整合完成。

**Independent Test**: 在已執行 Ollama 服務的環境中，修改設定檔後重啟後端，執行 `GET /health` 確認回應中 `backend` 欄位為 `ollama` 且 `status` 為 `ok`，即完成驗證。

**Acceptance Scenarios**:

1. **Given** Ollama 服務已在本機啟動且已拉取 `translategemma:4b` 模型，**When** 管理員將 `model.backend: "ollama"` 寫入 `config.yaml` 並重啟後端，**Then** `GET /health` 回應 `{"status": "ok", "backend": "ollama", "model": "translategemma:4b"}`
2. **Given** `model.backend: "local"` 為設定值（或設定檔未指定 backend 欄位），**When** 管理員未做任何變更，**Then** 後端行為與現行完全相同——使用行程內載入的本地模型，不呼叫任何外部服務
3. **Given** Ollama 服務未啟動，**When** 後端以 `ollama` 後端啟動並呼叫 `GET /health`，**Then** 回應 `status` 為 `error` 並包含連線失敗的說明訊息

---

### User Story 2 - 透過 Ollama 後端進行翻譯（含串流）(Priority: P2)

終端使用者透過前端介面送出翻譯請求，後端以 Ollama 推論並以串流方式回傳結果；使用者感受與現行 local 後端相同，無需感知後端類型。

**Why this priority**: 翻譯功能是服務的核心，需確認 Ollama 後端在串流與非串流模式均正確運作。

**Independent Test**: 以 `POST /api/translate` 送出翻譯請求（`stream: true` 及 `stream: false` 各一），驗證兩者均回傳正確翻譯結果且格式符合現有 API 規格。

**Acceptance Scenarios**:

1. **Given** Ollama 後端已啟動，**When** 以 `stream: false` 呼叫 `POST /api/translate`，**Then** 回傳完整翻譯結果 JSON，格式與 local 後端相同
2. **Given** Ollama 後端已啟動，**When** 以 `stream: true` 呼叫 `POST /api/translate`，**Then** 以 SSE 串流逐步回傳翻譯 token
3. **Given** 輸入文字超過 `translation.max_input_length` 上限，**When** 呼叫翻譯 API，**Then** 回傳 422 錯誤，錯誤格式與 local 後端一致
4. **Given** 翻譯逾時（超過 `translation.timeout`），**When** Ollama 推論未在時限內完成，**Then** 回傳逾時錯誤，串流連線正常關閉

---

### User Story 3 - 術語表與 Ollama 後端同時運作 (Priority: P3)

管理員啟用術語表（`glossary.enabled: true`）後，透過 Ollama 後端的翻譯結果需正確反映術語對照，行為與 local 後端完全相同。

**Why this priority**: 術語表是現有差異化功能，切換後端不得造成迴歸。

**Independent Test**: 在 `config.yaml` 中啟用術語表並定義至少一條術語，使用 Ollama 後端翻譯含該術語的句子，確認翻譯輸出採用指定譯詞。

**Acceptance Scenarios**:

1. **Given** 術語表啟用且含術語 `API → 應用程式介面`，**When** 透過 Ollama 後端翻譯含「API」的英文句子為繁體中文，**Then** 翻譯結果中出現「應用程式介面」
2. **Given** 術語表停用（`enabled: false`），**When** 呼叫 `GET /api/glossary`，**Then** 回傳 `{"enabled": false, "entries": []}`，不受後端類型影響
3. **Given** Ollama 後端運作中，**When** 呼叫 `GET /api/glossary`，**Then** 術語表資料正確回傳，與 local 後端行為相同

---

### Edge Cases

- Ollama 服務在翻譯過程中斷線，串流回應需正常終止並回報錯誤，不掛起連線。
- `ollama_model` 指定的模型名稱在 Ollama 中不存在：後端**啟動時**呼叫 `/api/tags` 驗證模型是否存在；若不存在則記錄 `WARNING` 並附上提示訊息（例如 `"請確認 Ollama 已拉取指定模型，或聯繫管理員執行 ollama pull {model}"`），後端仍繼續啟動（非硬性失敗）；首次翻譯請求時 Ollama 若仍回傳錯誤，以 500 錯誤回應並記錄 `ERROR` log。
- 同時存在 `local` 與 `ollama` 相關設定時，以 `model.backend` 的值為唯一依據，互不干擾。
- 超長輸入在截斷後仍需正確注入術語表內容。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系統必須在保留現有 local（行程內載入模型）後端架構完整不變的前提下，新增 `model.backend` 設定欄位（可選值 `local` / `ollama`），讓使用者透過修改設定檔並重啟服務自由選擇推論後端；預設值為 `local` 以確保既有部署無需任何改動
- **FR-002**: `ollama` 後端必須以 REST API 方式呼叫外部 Ollama 服務完成翻譯，不得於行程內載入模型檔案；呼叫目標為 Ollama 的聊天補全 REST 端點；`httpx.AsyncClient` 必須以單一實例共用（連線池），於 `OllamaBackend.__init__` 建立，FastAPI lifespan 結束時呼叫 `await client.aclose()` 關閉
- **FR-003**: 兩種後端均必須支援 SSE 串流回應，串流格式與現行規格完全相同；OllamaBackend 的串流結束信號必須與 local 後端的 `translate_stream` 所產生的格式完全一致，不得直接透傳 Ollama `/api/chat` 的原生結束信號
- **FR-004**: Prompt 組裝邏輯（包含術語表注入）必須在兩種後端均適用，且注入位置一致（system message）；OllamaBackend 的 system message 採純文字格式，以 `"You are a translation assistant. Translate the following text from {source_lang} to {target_lang}."` 結構指定語言對，不使用 TranslateGemma 專屬 chat template 的特殊欄位（`source_lang_code`、`target_lang_code` 等）
- **FR-005**: `GET /health` 必須回報目前使用的後端類型（`backend` 欄位）及連線狀態；Ollama 後端需額外回報 `ollama_url` 欄位
- **FR-006**: 輸入長度限制（`translation.max_input_length`）必須在 `ollama` 後端生效，超出時回傳與 local 後端相同格式的錯誤
- **FR-007**: Ollama HTTP 請求的逾時時間必須採用 `translation.timeout` 設定值
- **FR-008**: `POST /api/translate`、`GET /api/languages`、`GET /api/glossary`、`GET /health` 等端點的 API 介面契約不得因後端切換而改變
- **FR-009a**: 使用者必須能在 `config.yaml` 的 `model.ollama_base_url` 欄位自行指定 Ollama REST API 服務的完整位址（例如 `http://192.168.1.10:11434`），預設為 `http://localhost:11434`
- **FR-009b**: 使用者必須能在 `config.yaml` 的 `model.ollama_model` 欄位自行指定 Ollama 中已拉取的模型名稱（例如 `translategemma:12b`），預設為 `translategemma:4b`
- **FR-010**: `local` 後端的既有程式碼與行為（模型自動偵測裝置、dtype 選擇、本地路徑解析、啟動載入邏輯）不得因本次變更而改變，`model.backend` 預設為 `local` 以確保向下相容

### Non-Functional Requirements

- **NFR-001（可觀察性）**: OllamaBackend 於發生例外時（連線錯誤、逾時、模型不存在等），必須以 `logging.error(...)` 記錄結構化訊息，欄位至少含 `backend`、`error_type`、`message`；正常推論路徑不額外輸出 log，使用現有 Python `logging` 模組，不引入新依賴
- **NFR-002（資源管理）**: `httpx.AsyncClient` 必須以單一實例共用（連線池），不得每次請求重新建立；實例於 `OllamaBackend.__init__` 建立，FastAPI lifespan 結束時呼叫 `await client.aclose()` 釋放

### Key Entities

- **TranslationBackend**（後端抽象介面）：定義翻譯服務的統一契約，包含翻譯（單次）與串流翻譯兩種操作；所有具體後端均須實作此介面
- **LocalBackend**：**現有**後端實作，架構保持不變；於行程內直接載入本地模型檔案進行推論，`model.backend: "local"` 時啟用
- **OllamaBackend**：**新增**後端實作；以 REST API 方式呼叫外部 Ollama 服務完成推論，`model.backend: "ollama"` 時啟用；持有兩項使用者可設定的參數：Ollama 服務位址（URL）與目標模型名稱
- **GlossaryEntry**（現有）：術語對照項目；在 Prompt 組裝層被注入 system message，與後端類型無關

## Assumptions

- 使用者自行安裝並管理 Ollama 服務，後端不負責安裝或啟動 Ollama。
- Ollama 服務與後端服務位於同一受信任網路，無需額外認證機制。
- `translategemma:4b` 模型已由使用者在 Ollama 中事先拉取（`ollama pull translategemma:4b`）。
- Ollama 的聊天補全 API 格式符合標準 `/api/chat` 介面，接受 messages 陣列並支援串流選項。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 管理員可在修改設定檔並重啟後端後 5 分鐘內完成後端切換，無需修改任何程式碼
- **SC-002**: 使用 Ollama 後端的翻譯 API（串流與非串流）回應格式與 local 後端 100% 一致，原有前端無需任何修改
- **SC-003**: 術語表功能在 Ollama 後端的正確率與 local 後端相同，涵蓋術語注入、停用狀態、查詢端點三個場景
- **SC-004**: 切換後端後，所有現有整合測試（API 契約、術語表、語言清單、健康檢查）通過率維持 100%
- **SC-005**: Ollama 服務連線失敗時，健康檢查端點在 3 秒內回傳明確錯誤狀態，不掛起請求

## Clarifications

### Session 2026-04-12

- Q: OllamaBackend 的 Prompt 語言指示格式為何？ → A: System message 採純文字格式：`"You are a translation assistant. Translate the following text from {source_lang} to {target_lang}."`，不使用 TranslateGemma chat template 的特殊欄位
- Q: OllamaBackend 失敗時應記錄何種層級與格式的 log？ → A: `logging.error(...)` 記錄含 `backend`、`error_type`、`message` 欄位的結構化訊息，僅在例外發生時記錄，使用現有 Python logging 模組
- Q: `ollama_model` 不存在應於何時偵測？ → A: 啟動時呼叫 `/api/tags` 驗證；模型不存在記錄 `WARNING` 並附上提示管理員執行 `ollama pull {model}` 的訊息，後端繼續啟動（非硬性失敗）；首次翻譯失敗時再記錄 `ERROR`
- Q: OllamaBackend 串流結束信號格式為何？ → A: 必須與 local 後端 `translate_stream` 產生的格式完全一致，不透傳 Ollama 原生結束信號，由 OllamaBackend 自行轉換
- Q: `httpx.AsyncClient` 應每次請求建立還是共用？ → A: 單一實例共用（連線池），於 `OllamaBackend.__init__` 建立，FastAPI lifespan 結束時 `await client.aclose()` 關閉
