# Tasks: 後端整合 Ollama 模型管理

**Input**: Design documents from `/specs/001-ollama-backend/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/health-api.yaml ✅

**Tests**: 依 plan.md Constitution Principle IV（測試先行），本功能包含單元測試與整合測試任務。

**Organization**: 任務依使用者故事分組，每個故事可獨立實作與驗證。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可平行執行（不同檔案、無相互依賴）
- **[Story]**: 所屬使用者故事（US1/US2/US3）
- 每項任務均含精確檔案路徑

---

## Phase 1: Setup（基礎準備）

**Purpose**: 新增依賴與設定範例，為後續實作建立環境基礎

- [X] T001 確認並新增 `httpx` 至 `backend/requirements.txt`（若未列入則加入，保留現有套件不變）
- [X] T002 [P] 補充 `config.example.yaml`：在 `model:` 區段新增 `backend`、`ollama_base_url`、`ollama_model` 欄位說明與預設值範例

---

## Phase 2: Foundational（核心抽象層，阻塞所有故事）

**Purpose**: 建立後端抽象介面與工廠函式，所有使用者故事均依賴此階段完成

**⚠️ CRITICAL**: 此階段必須全部完成，使用者故事實作才能開始

- [X] T003 建立 `backend/src/backends/base.py`：定義 `TranslationBackend` ABC
- [X] T004 [P] 修改 `backend/src/config.py`：新增三個 `setdefault`
- [X] T005 建立 `backend/src/backends/local.py`：`LocalBackend`
- [X] T006 建立 `backend/src/backends/__init__.py`：`create_backend()` 工廠函式

**Checkpoint**: 抽象層就緒，可開始 US1 實作

---

## Phase 3: User Story 1 — 管理員選擇 Ollama 後端 (Priority: P1) 🎯 MVP

**Goal**: 管理員透過 `config.yaml` 選擇 `local` 或 `ollama` 後端；`GET /health` 正確回報後端類型與連線狀態

**Independent Test**: 分別以 `model.backend: "local"` 與 `model.backend: "ollama"` 啟動後端，呼叫 `GET /health` 確認回應含正確 `backend` 欄位；Ollama 服務離線時 `status` 為 `error`

### 測試（US1）

- [X] T007 [P] [US1] 新增 `backend/tests/unit/test_ollama_backend.py`：撰寫 `health_info` 測試
- [X] T008 [US1] 建立 `backend/src/backends/ollama.py`：`OllamaBackend`
- [X] T009 [US1] `OllamaBackend.startup()` 啟動驗證
- [X] T010 [P] [US1] `OllamaBackend.health_info()`
- [X] T011 [US1] 修改 `backend/src/main.py`：lifespan 改用 `create_backend()`
- [X] T012 [US1] 修改 `backend/src/routes/health.py`：新增 `backend`/`ollama_url` 欄位

**Checkpoint**: 此時 User Story 1 可獨立驗證——`GET /health` 正確回報後端類型

---

## Phase 4: User Story 2 — 透過 Ollama 後端翻譯（含串流）(Priority: P2)

**Goal**: `POST /api/translate` 透過 Ollama 後端完成翻譯（非串流與 SSE 串流），回應格式與 local 後端 100% 相同

**Independent Test**: 以 `stream: false` 及 `stream: true` 各呼叫一次 `POST /api/translate`，驗證回應格式符合現有 API 規格；逾時時回傳錯誤且串流正常關閉

### 測試（US2）

- [X] T013 [P] [US2] 擴充 `backend/tests/unit/test_ollama_backend.py`：新增 `translate` 測試（mock `httpx.AsyncClient.post` 非串流回應，驗證解析結果）、`translate_stream` 測試（mock NDJSON 串流，驗證 token yield 順序與串流結束格式）、逾時測試（mock `httpx.TimeoutException`，驗證 `logging.error` 被呼叫）

### 實作（US2）

- [X] T014 [P] [US2] 實作 `OllamaBackend._build_messages(text, source_lang, target_lang) -> list[dict]`：組裝純文字 system message（`"You are a translation assistant. Translate the following text from {source_lang} to {target_lang}."`）與 user message（`text`）
- [X] T015 [US2] 實作 `OllamaBackend.translate()`：呼叫 `POST /api/chat`（`stream: false`），以 `translation.timeout` 設定 `httpx.AsyncClient` 逾時；解析 Ollama 回應並回傳翻譯文字；發生例外時以 `logging.error()` 記錄結構化訊息後重新拋出
- [X] T016 [US2] 實作 `OllamaBackend.translate_stream()`：呼叫 `POST /api/chat`（`stream: true`）；逐行解析 NDJSON，yield 每個 token；串流結束信號格式必須與 `LocalBackend.translate_stream` 一致（對齊現有 local 後端格式，不直接透傳 Ollama 原生結束信號）；Ollama 中途斷線時正常終止並記錄 `ERROR` log
- [X] T017 [US2] 擴充 `backend/tests/integration/test_api_endpoints.py`：新增 mock Ollama 後端場景——`stream: false` 翻譯回傳正確 JSON、`stream: true` 回傳 SSE 事件流、輸入超過 `max_input_length` 回傳 422、逾時回傳 500

**Checkpoint**: 此時 User Stories 1 與 2 均可獨立驗證

---

## Phase 5: User Story 3 — 術語表與 Ollama 後端同時運作 (Priority: P3)

**Goal**: 啟用術語表後，透過 Ollama 後端翻譯結果正確反映術語對照；`GET /api/glossary` 不受後端類型影響

**Independent Test**: 啟用術語表並定義至少一條術語，使用 Ollama 後端翻譯含該術語的句子，確認翻譯輸出採用指定譯詞；另呼叫 `GET /api/glossary` 確認回傳正確

### 測試（US3）

- [X] T018 [P] [US3] 擴充 `backend/tests/unit/test_ollama_backend.py`：新增術語注入驗證——確認路由層 `_apply_glossary_preprocess` 預處理後的文字正確傳入 `OllamaBackend.translate`，且 `_build_messages` 產生的 user message 含替換後術語

### 實作（US3）

- [X] T019 [US3] 確認 `backend/src/routes/translate.py` 的 `_apply_glossary_preprocess` 呼叫鏈在切換後端後仍正確運作（trace 程式流程，若有後端型別相依則移除）；`routes/translate.py` 介面不得改變
- [X] T020 [US3] 擴充 `backend/tests/integration/test_api_endpoints.py`：新增術語表 + Ollama 後端場景——`GET /api/glossary` 回傳正確（`enabled: true/false`）；翻譯含術語文字時輸出含指定譯詞；術語停用時行為正確

**Checkpoint**: 三個使用者故事均可獨立驗證

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 確認整合完整性、驗證現有測試未迴歸

- [X] T021 [P] 執行完整測試套件 `pytest backend/tests/` 確認所有現有測試通過（57/57 通過）
- [X] T022 [P] 依照 `specs/001-ollama-backend/quickstart.md` 步驟手動驗證：嗟用 Ollama 後端、呼叫 `GET /health`、執行非串流翻譯、執行串流翻譯
- [X] T023 驗證 `model.backend` 未設定時（或設定為 `local`）後端行為與現行完全相同（向下相容確認）

---

## Dependencies & Execution Order

### Phase 依賴關係

- **Phase 1（Setup）**：無依賴，可立即開始
- **Phase 2（Foundational）**：依賴 Phase 1 完成；**阻塞所有使用者故事**
- **Phase 3（US1）**：依賴 Phase 2 完成；無其他故事依賴
- **Phase 4（US2）**：依賴 Phase 2 完成；US2 任務可與 US1 並行（不同檔案）
- **Phase 5（US3）**：依賴 Phase 2 完成；技術上可與 US1/US2 並行，但建議 US2 完成後再執行
- **Phase 6（Polish）**：依賴所有使用者故事完成

### 使用者故事依賴關係

- **US1（P1）**：Phase 2 完成後可開始，無其他故事依賴
- **US2（P2）**：Phase 2 完成後可開始；`_build_messages`（T014）需先於 `translate`（T015）、`translate_stream`（T016）完成
- **US3（P3）**：Phase 2 完成後可開始；建議 US2 完成後再執行以確保翻譯基礎可用

### 任務內部依賴

```
T001 → T006（requirements 確認後，工廠函式才能完整引用 OllamaBackend）
T003 → T005 → T006（ABC → LocalBackend → create_backend 工廠）
T003 → T008 → T010（ABC → OllamaBackend shell → health_info）
T006 → T011（工廠函式 → main.py lifespan）
T010 → T012（health.py 依賴 health_info 回傳格式）
T014 → T015 → T016（_build_messages → translate → translate_stream）
T015, T016 → T017（OllamaBackend 翻譯方法 → 整合測試）
T019 → T020（路由層確認 → 整合測試）
```

---

## Parallel Execution Examples

### Phase 2 並行範例

可同步進行：
```
T003 建立 base.py (TranslationBackend ABC)
T004 修改 config.py (setdefault 新增)
```
T003 完成後繼續 T005 → T006。

### US1 並行範例

```
T007 撰寫 health_info 單元測試    ← 可先行
T008 建立 OllamaBackend.__init__  ← 可先行
```
T008 完成後繼續 T009（startup 驗證）→ T010（health_info 實作）→ T012（health.py 修改）。

### US2 並行範例

```
T013 撰寫翻譯單元測試     ← [P] 可先行（測試先行）
T014 實作 _build_messages ← [P] 可先行
```
T014 完成後繼續 T015 → T016 → T017。

---

## Implementation Strategy

### MVP 範圍（建議最小可交付增量）

**僅實作 Phase 1 + Phase 2 + Phase 3（US1）**即可交付 MVP：
- 管理員可透過 `config.yaml` 切換後端
- `GET /health` 正確回報後端類型與連線狀態
- local 後端行為完全不受影響

### 增量交付建議

1. **MVP**：Phase 1 → Phase 2 → Phase 3（US1）
2. **翻譯功能**：+Phase 4（US2）
3. **完整功能**：+Phase 5（US3）+ Phase 6（Polish）

---

## Summary

| 指標 | 數值 |
|------|------|
| 任務總數 | 23 |
| Phase 1（Setup） | 2 |
| Phase 2（Foundational） | 4 |
| Phase 3（US1） | 6 |
| Phase 4（US2） | 5 |
| Phase 5（US3） | 3 |
| Phase 6（Polish） | 3 |
| 可平行任務（[P]） | 9 |
| 新增檔案 | 5（base.py, local.py, ollama.py, \_\_init\_\_.py, test_ollama_backend.py） |
| 修改檔案 | 6（config.py, main.py, health.py, test_api_endpoints.py, requirements.txt, config.example.yaml） |

**MVP 範圍**：US1（Phase 1+2+3，12 項任務）
**並行機會**：Phase 2 的 T003/T004 可並行；US2 的 T013/T014 可並行；US3 的 T018/T019 可並行
