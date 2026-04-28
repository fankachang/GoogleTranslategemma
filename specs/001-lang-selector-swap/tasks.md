# Tasks: 語系選擇器與互換功能

**Input**: Design documents from `/specs/001-lang-selector-swap/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Branch**: `001-lang-selector-swap`  
**Date**: 2026-04-28

## Format: `[ID] [P?] [Story?] 說明 in 檔案路徑`

- **[P]**: 可平行執行（不同檔案，無未完成的依賴）
- **[US1/US2/US3]**: 所屬 User Story
- 每個任務包含精確的檔案路徑

---

## Phase 1: Setup（共用設定）

**Purpose**: 在設定檔新增 features 區塊，確認環境正確

- [ ] T001 新增 `features.language_selector: false` 至 config.yaml（根目錄）
- [ ] T002 [P] 新增 `features.language_selector: false` 說明至 config.example.yaml（根目錄）

**Checkpoint**: config.yaml / config.example.yaml 含 features 區塊

---

## Phase 2: Foundational（阻斷性基礎建設）

**Purpose**: 前後端共用的基礎型別與設定載入，所有 User Story 均依賴此 Phase

**⚠️ CRITICAL**: 所有 User Story 的實作工作必須等此 Phase 完成後才可開始

- [ ] T003 擴充 `backend/src/config.py` 的 `load_config()` 新增巢狀 setdefault — `config.setdefault("features", {}); config["features"].setdefault("language_selector", False)`
- [ ] T004 [P] 改寫 `frontend/Models/AppConfigResponse.cs` 為 init-only properties 並新增 `FeaturesConfig` record（`language_selector` 預設 `false`）
- [ ] T005 [P] 擴充 `frontend/AppConfig.cs` 新增 `LanguageSelectorEnabled bool` 屬性（預設 `false`）

**Checkpoint**: 基礎建設就緒，可開始各 User Story 的平行實作

---

## Phase 3: User Story 1 — 管理員透過設定檔啟用語系選擇器（Priority: P1）🎯 MVP

**Goal**: 管理員修改 `config.yaml` 後重啟，前端能正確讀取 `features.language_selector` 旗標。

**Independent Test**: 設定 `features.language_selector: true`，`GET /api/config` 應回傳 `{ "features": { "language_selector": true } }`；設為 `false` 應回傳 `false`。

### 測試（Test-First — 先寫測試確認失敗，再實作）

- [ ] T006 [P] [US1] 建立 `backend/tests/unit/test_config_features.py`：測試 `load_config()` 在 `features` 區塊缺失時預設 `False`、非布林值時回退 `False`
- [ ] T007 [P] [US1] 建立 `backend/tests/integration/test_api_config.py`：測試 `GET /api/config` 回傳含 `features.language_selector` 的 JSON 結構（`true` / `false` 兩種情境）

### 實作

- [ ] T008 [US1] 擴充 `backend/src/routes/config.py` 的 `get_config()` 回傳 `features.language_selector`，含型別驗證（非 bool 回退 `False`）
- [ ] T009 [US1] 在 `.venv` 環境下執行 `pytest backend/tests/unit/test_config_features.py backend/tests/integration/test_api_config.py -v` 確認所有測試通過

**Checkpoint**: `GET /api/config` 正確回傳 `features.language_selector`，後端完整可獨立測試

---

## Phase 4: User Story 2 — 使用者手動選擇原語系與目的語系（Priority: P1）

**Goal**: 啟用語系選擇器後，UI 顯示「原語系 ↔ 目的語系」列，使用者選擇後翻譯請求攜帶正確 `source_lang` / `target_lang`。

**Independent Test**: 啟用語系選擇器，選擇「英文」→「繁體中文」，送出翻譯後 Network 面板應顯示請求含 `source_lang: "en"`, `target_lang: "zh-TW"`；頁面初始狀態兩側均為「自動偵測」。

### 實作

- [ ] T010 [US2] 確認 `frontend/Program.cs` 已注入 `LanguageService`（若未注入則新增 `builder.Services.AddScoped<LanguageService>()`）
- [ ] T011 [US2] 在 `frontend/Pages/Index.razor` 的 `OnInitializedAsync` 新增呼叫 `GET /api/config` 邏輯，解析 `AppConfigResponse.Features.LanguageSelector` 並寫入 `AppCfg.LanguageSelectorEnabled`；失敗時 catch 並記錄 `console.error`，回退 `false`
- [ ] T012 [P] [US2] 在 `frontend/Pages/Index.razor` `@code` 新增語系狀態變數：`sourceLang`（`string?`）、`targetLang`（`string?`）、`languages`（`List<Language>`）、`isLangLoading`（`bool`）
- [ ] T013 [US2] 在 `frontend/Pages/Index.razor` `OnInitializedAsync` 新增呼叫 `LanguageService.GetLanguagesAsync()`：**呼叫前設 `isLangLoading = true`**；try/finally 確保完成後設 `isLangLoading = false`；成功時設定 `languages` 清單，失敗時 `console.error` 並讓 `languages` 保持空清單（觸發隱藏邏輯）
- [ ] T014 [US2] 在 `frontend/Pages/Index.razor` 固定底部輸入區 `<div>` 內、`<TranslationInput>` 之前，插入語系選擇器列（`@if (AppCfg.LanguageSelectorEnabled && languages.Count > 0)`），寬度與 `ContentWidthPercent` 對齊，包含兩個 `<LanguageSelector>` 與佔位互換按鈕
- [ ] T015 [US2] 在 `frontend/Pages/Index.razor` 實作 `OnSourceLangChanged` / `OnTargetLangChanged` 事件處理，含 FR-009 雙向自動切換邏輯（選 `zh-TW` → 另一側變 `en`；選 `en` → 另一側變 `zh-TW`；條件：另一側為 `null` 或與剛選的相同）
- [ ] T016 [US2] 在 `frontend/Pages/Index.razor` 語系選擇器列新增 FR-008 inline 警告：當 `sourceLang != null && targetLang != null && sourceLang == targetLang` 時顯示 `<MudAlert>` 警告文字
- [ ] T017 [US2] 在 `frontend/Pages/Index.razor` 確認 `LanguageSelector` 元件在 `isLangLoading == true` 時套用 `Disabled` 屬性（FR-010 載入中停用狀態）
- [ ] T018 [US2] 在 `frontend/Pages/Index.razor` 的 `HandleSubmit`：語系選擇器**啟用時**傳入 `sourceLang` / `targetLang`（`null` = 自動偵測）；**停用時繼續呼叫 `DetectTargetLang()`**，不傳 `sourceLang`/`targetLang`，對現有自動偵測行為無影響

**Checkpoint**: 語系選擇器 UI 完整可用：顯示/隱藏由 config 控制、FR-008/FR-009/FR-010 均正確運作、翻譯請求帶正確語系值

---

## Phase 5: User Story 3 — 使用者點擊互換按鈕交換原語系與目的語系（Priority: P2）

**Goal**: 點擊 ↔ 按鈕後兩側語系值純粹互換，不觸發 FR-009 自動切換邏輯。

**Independent Test**: 設原語系「繁體中文」、目的語系「英文」，點擊 ↔，原語系應變「英文」、目的語系應變「繁體中文」；再點一次應還原。

### 實作

- [ ] T019 [US3] 在 `frontend/Pages/Index.razor` 實作 `SwapLanguages()` 方法：直接交換 `sourceLang` 與 `targetLang` 的值，不呼叫 `OnSourceLangChanged` / `OnTargetLangChanged`，不觸發 FR-009
- [ ] T020 [US3] 在 Phase 4 T013 所插入的語系選擇器列中，將互換按鈕的 `OnClick` 綁定至 `SwapLanguages()`，`Disabled="@(isLangLoading || !AppCfg.LanguageSelectorEnabled)"`

**Checkpoint**: 所有 User Story 均完整可獨立運作

---

## Phase 6: Polish & 橫切面關注點

**Purpose**: 可觀察性補強、前端測試與最終驗證

- [ ] T021 [P] 審查 `frontend/Pages/Index.razor` 所有 catch 路徑，確認 `GET /api/config` 與 `GET /api/languages` 失敗均有 `console.error` 記錄（Principle VII）
- [ ] T022 [P] [US2] 新增 `frontend/Pages/Index.razor` 前端自動化測試：使用 `dotnet test` 驗證語系選擇器 UI 主要狀態（啟用/隱藏、FR-008 警告、FR-010 停用狀態）；若前端 dotnet test 基礎設施尚未建立，需先完成基礎機制建立
- [ ] T023 依 `specs/001-lang-selector-swap/quickstart.md` 執行完整手動驗證：`features.language_selector: true` 情境（顯示選擇器）與 `false` 情境（隱藏選擇器，自動偵測模式正常）

---

## Dependencies & Execution Order

### Phase 依賴

- **Setup (Phase 1)**：無依賴，立即可開始
- **Foundational (Phase 2)**：依賴 Phase 1 完成 — 阻斷所有 User Story
- **US1 (Phase 3)**：依賴 Phase 2 完成 — 與 US2/US3 可平行
- **US2 (Phase 4)**：依賴 Phase 2 完成；建議 US1 先行（確保後端 API 可用）
- **US3 (Phase 5)**：依賴 Phase 4 完成（需要 Phase 4 建立的狀態變數與語系列 DOM 結構）
- **Polish (Phase 6)**：依賴所有目標 User Story 完成

### User Story 依賴

- **US1 (P1)**：Phase 2 完成後即可開始，無其他依賴
- **US2 (P1)**：Phase 2 完成後可開始；US1 提供可用的後端 API，建議 US1 先行但非強制
- **US3 (P2)**：依賴 US2 語系列 DOM 結構，不可平行

### 各 User Story 內部執行順序

```
US1: T006 [P] ─┐
               ├─ T008 → T009
T007 [P] ──────┘

US2: T010 → T011 [P] ─┐
                      ├─ T013 → T014 → T015 → T016 → T017 → T018
T012 ─────────────────┘

US3: T019 → T020
```

### 平行執行機會

- T001 + T002：Phase 1 可平行
- T004 + T005：Phase 2 可平行（不同檔案）
- T006 + T007：US1 測試可平行撰寫
- T011 + T012：US2 狀態變數與語系清單載入可平行

---

## 平行執行範例：User Story 1

```bash
# 1. 先確保 Phase 2 完成
# 2. 同時建立測試檔案（T006, T007）
# 終端 A
code backend/tests/unit/test_config_features.py

# 終端 B
code backend/tests/integration/test_api_config.py

# 3. 確認測試失敗後，實作後端（T008）
# 4. 執行測試確認通過（T009）
```

## 平行執行範例：User Story 2

```bash
# T010 (OnInitializedAsync config) 與 T011+T012 (狀態變數 + 語系載入) 可依序但快速完成
# T013 開始前需要 T011, T012 已完成（狀態變數存在）
# T014-T017 均在同一檔案內，循序執行
```

---

## Implementation Strategy

**MVP 範疇（最小可驗證產品）**：完成 Phase 1 + Phase 2 + Phase 3（US1）即可驗證後端完整功能；Phase 4（US2）完成後 MVP 對使用者可見。

**交付順序建議**：
1. Phase 1 + 2（Setup + Foundation）— 約 3 個任務，無阻礙
2. Phase 3（US1）— 後端 4 個任務，含測試，獨立可驗證
3. Phase 4（US2）— 前端 9 個任務，依賴後端 API 可用
4. Phase 5（US3）— 前端 2 個任務，依賴 US2 佈局
5. Phase 6（Polish）— 2 個任務，最終收尾

---

## Task Summary

| Phase | 對應 Story | 任務數 | 說明 |
|---|---|---|---|
| Phase 1: Setup | — | 2 | config.yaml / config.example.yaml |
| Phase 2: Foundational | — | 3 | backend config.py + frontend DTO + AppConfig |
| Phase 3 | US1 (P1) | 4 | 後端 API 擴充 + pytest 測試 |
| Phase 4 | US2 (P1) | 9 | 前端語系選擇器 UI 完整整合 |
| Phase 5 | US3 (P2) | 2 | 互換按鈕邏輯 |
| Phase 6: Polish | — | 3 | 可觀察性 + 前端測試 + 最終驗證 |
| **合計** | | **23** | |

### 平行機會

| 可平行組 | 任務 |
|---|---|
| Phase 1 | T001 + T002 |
| Phase 2 | T004 + T005（與 T003 平行） |
| US1 測試 | T006 + T007 |
| Polish | T021（不依賴 T022） |

### 各 User Story 獨立測試標準

| Story | 測試標準 |
|---|---|
| US1 | `GET /api/config` 回傳 `features.language_selector`，pytest 全數通過 |
| US2 | 選擇語系後翻譯請求含正確 `source_lang`/`target_lang`；FR-008/FR-009/FR-010 均通過人工驗證 |
| US3 | 點擊 ↔ 兩側值互換，不觸發自動切換；載入中時按鈕 disabled |

### 建議 MVP 範疇

完成 Phase 1 + Phase 2 + Phase 3（US1）+ Phase 4（US2）= 18 個任務（T001–T018）  
→ 此時功能完整對使用者可見，US3 互換按鈕（T019–T020）為加分功能可獨立後補。
