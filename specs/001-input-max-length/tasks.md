# Tasks: 可設定的翻譯輸入字數上限

**Feature Branch**: `001-input-max-length`  
**Input**: Design documents from `/specs/001-input-max-length/`  
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/api-config.yaml ✅ quickstart.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.  
**Tests**: Not included（本 tasks.md 未包含測試任務；如需新增 `test_config_route.py` / `test_translate_limit.py`，請重新產生並指定 TDD 模式）

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel（不同檔案、無未完成依賴）
- **[Story]**: US1 = 前端即時字數提示 | US2 = config.yaml 可設定 | US3 = 後端請求驗證

---

## Phase 1: Setup（設定檔初始化）

**Purpose**: 新增 `max_input_length` 欄位至所有設定檔，作為後端讀取的資料來源起點

- [ ] T001 [P] 在 `config.yaml` 的 `translation` 區段新增 `max_input_length: 512`
- [ ] T002 [P] 在 `config.example.yaml` 的 `translation` 區段新增 `max_input_length: 512`（與 T001 保持同步）

---

## Phase 2: Foundational（後端設定載入基礎）

**Purpose**: 後端 `load_config()` 加入 `max_input_length` 預設值與合法性驗證，供所有後端路由與前端 API 使用

**⚠️ CRITICAL**: Phase 3 / Phase 4 / Phase 5 中所有依賴 `app.state.config` 的後端工作均需等待此 Phase 完成

- [ ] T003 在 `backend/src/config.py` 的 `load_config()` 中以 `setdefault` 補入 `translation.max_input_length = 512`，並加入驗證：若值 ≤ 0 或非整數則強制覆寫為 `512`（依賴 T001）

**Checkpoint**: 後端設定基礎就緒 — US1 前端 / US2 API 端點 / US3 路由驗證可並行開始

---

## Phase 3: User Story 1 — 前端即時字數提示與限制（Priority: P1）🎯 MVP

**Goal**: 輸入框下方即時顯示「目前字數 / 上限字數」，超限時計數器以 MudBlazor `Color.Error` 顯示並停用送出按鈕，刪回上限以內後自動恢復

**Independent Test**: 開啟網頁，在輸入框輸入任意文字，觀察字數計數器是否即時更新（≤ 100 ms）；輸入字元數超過上限時計數器應變紅、送出按鈕應停用；刪回上限以內後按鈕應恢復可用。無需後端 `/api/config` 就緒（預設值 512）

### Implementation for User Story 1

- [ ] T004 [P] [US1] 在 `frontend/AppConfig.cs` 新增 `public int MaxInputLength { get; set; } = 512;` 屬性（預設值防止 `Program.cs` 取值前元件崩潰）
- [ ] T005 [P] [US1] 在 `frontend/Components/TranslationInput.razor` 新增 `[Parameter] public int MaxInputLength { get; set; } = 512;`，取代所有硬碼 `5000`，實作字數計數顯示（`@Text.Length / @MaxInputLength`）、超限警告色（`Color.Error`）、超限停用送出按鈕，及 `Submit()` early-return 防護（依賴 T004 介面確認）
- [ ] T006 [US1] 在 `frontend/Pages/Index.razor` 對 `<TranslationInput>` 元件加入 `MaxInputLength="@AppCfg.MaxInputLength"` 屬性傳遞（依賴 T004、T005）

**Checkpoint**: US1 完成。使用預設值 512 可完整測試所有前端字數限制行為，無需等待 US2

---

## Phase 4: User Story 2 — 管理員透過 config.yaml 設定字數上限（Priority: P2）

**Goal**: 管理員修改 `config.yaml` 並重啟服務後，前後端皆套用新上限值，無需修改任何程式碼（FR-006 單一設定來源）

**Independent Test**: 修改 `config.yaml` 中的字數上限為 256，重啟服務後執行 `curl http://localhost:8000/api/config`，確認回傳 `{"max_input_length": 256}`；開啟網頁確認輸入框上限顯示為 256，且輸入 257 個字元時送出按鈕被停用

### Implementation for User Story 2

- [ ] T007 [P] [US2] 新增 `backend/src/routes/config.py`：定義 `AppConfigResponse(BaseModel)` 含 `max_input_length: int`，實作 `GET /api/config` 端點回傳 `AppConfigResponse(max_input_length=request.app.state.config["translation"]["max_input_length"])`；端點無需驗證（FR-010，`security: []`）（依賴 T003）
- [ ] T008 [US2] 在 `backend/src/main.py` 加入 `from src.routes.config import router as config_router` 並呼叫 `app.include_router(config_router, prefix="/api")`（依賴 T007）
- [ ] T009 [US2] 在 `frontend/Program.cs` 於 `builder.Build()` 前以 `try/catch` 包裹 `HttpClient.GetFromJsonAsync<AppConfigResponse>("/api/config")`：成功時更新 `appConfig.MaxInputLength`；失敗時 `Console.Error.WriteLine` 靜默記錄並保留預設值 `512`，不阻擋應用啟動（FR-011）（依賴 T004、T008）

**Checkpoint**: US2 完成。`config.yaml` 修改 `max_input_length` 並重啟，前後端均套用新值

---

## Phase 5: User Story 3 — 後端拒絕超出上限的請求（Priority: P3）

**Goal**: 即使前端被繞過直接呼叫 API，後端亦回傳 HTTP 422 並附帶可讀錯誤訊息，前端收到後在對話介面顯示友善錯誤提示（FR-007）

**Independent Test**: 透過 API 工具直接向 `POST /api/translate` 送出含 513 個字元的請求，確認後端回傳 `422` 及 `{"detail": "輸入文字超過允許上限（512 字元）"}`；送出恰好 512 字元應回傳 `200`（邊界值被接受）

### Implementation for User Story 3

- [ ] T010 [P] [US3] 在 `backend/src/schemas/translation.py` 將 `TranslationRequest.text` 的 `max_length` 由 `5000` 改為 `10000`（Pydantic 硬上限防濫用；業務上限由 route 層動態驗證）
- [ ] T011 [US3] 在 `backend/src/routes/translate.py` 的 `translate_endpoint` 中，Pydantic 驗證通過後加入業務長度驗證：讀取 `limit = request.app.state.config["translation"]["max_input_length"]`，若 `len(req.text) > limit` 則 `raise HTTPException(status_code=422, detail=f"輸入文字超過允許上限（{limit} 字元）")`（依賴 T003、T010）

**Checkpoint**: US3 完成。三個 User Story 均可獨立測試與部署

---

## Phase 6: Polish & 驗收確認

**Purpose**: 端對端驗收，確認所有 User Story 整合後行為符合 quickstart.md 場景

- [ ] T012 依照 `specs/001-input-max-length/quickstart.md` 執行完整驗收流程：預設值 512 驗證 → 修改設定為 256 並重啟驗證 → 前端 UI 行為驗證 → 模擬 `/api/config` 失敗驗證回退（依賴 T001–T011 全部完成）

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1（Setup）**: 無依賴，立即開始
- **Phase 2（Foundational）**: 依賴 Phase 1 — **阻擋所有後端路由工作**
- **Phase 3（US1）**: 依賴 Phase 2；不依賴 US2 / US3，可獨立交付
- **Phase 4（US2）**: 依賴 Phase 2 + T004；T007 可與 US1 並行
- **Phase 5（US3）**: 依賴 Phase 2；T010 可與 US1 / US2 並行
- **Phase 6（Polish）**: 依賴所有前序 Phase 完成

### User Story Dependencies

| Story | 先決條件 | 可獨立測試 | 說明 |
|-------|---------|-----------|------|
| US1 (P1) | Phase 2 完成 | ✅ | 使用預設值 512，不需後端 `/api/config` 就緒（FR-011） |
| US2 (P2) | Phase 2 + T004 完成 | ✅ | `curl /api/config` 驗證後端；頁面重載驗證前端 |
| US3 (P3) | Phase 2 完成 | ✅ | 直接以 API 工具呼叫，不依賴前端 |

### Within Each User Story

- **US1**: T004 [P] + T005 [P] 可並行 → T006 需等 T004 + T005
- **US2**: T007 [P] 獨立 → T008 等 T007 → T009 等 T004 + T008
- **US3**: T010 [P] 獨立 → T011 等 T003 + T010

### Task-Level Dependency Graph

```
T001 ──┐
T002 ──┘ (Phase 1 parallel)
        ↓
      T003 (Phase 2, 阻擋後端路由)
      ↙    ↘         ↘
   T004     T007      T010
   T005     ↓          ↓
   ↓       T008       T011
  T006      ↓
           T009 (需 T004 + T008)
```

---

## Parallel Example: Phase 2 完成後

```
# Phase 2（T003）完成後可同時開啟以下批次：

批次 A — US1 前端（並行）:
  T004: frontend/AppConfig.cs
  T005: frontend/Components/TranslationInput.razor

批次 B — US2 後端端點（與批次 A 同時）:
  T007: backend/src/routes/config.py

批次 C — US3 Schema（與批次 A + B 同時）:
  T010: backend/src/schemas/translation.py

# 批次 A 完成後:
  T006: frontend/Pages/Index.razor

# T007 完成後:
  T008: backend/src/main.py

# T004 + T008 完成後:
  T009: frontend/Program.cs

# T003 + T010 完成後:
  T011: backend/src/routes/translate.py

# T001–T011 全部完成後:
  T012: quickstart.md 驗收
```

---

## Implementation Strategy

### MVP First（僅 User Story 1，固定 512）

1. 完成 Phase 1: Setup（T001、T002）
2. 完成 Phase 2: Foundational（T003）— **CRITICAL**
3. 完成 Phase 3: US1（T004 [P] + T005 [P] → T006）
4. **STOP & VALIDATE**: 前端顯示 `0 / 512`、超限變紅、按鈕停用 ✅
5. 可先部署或展示此 MVP

### Incremental Delivery

1. Phase 1 + Phase 2 → 後端設定基礎就緒
2. Phase 3（US1）→ 前端字數限制可用 → **Demo MVP**
3. Phase 4（US2）→ `config.yaml` 設定生效，前後端同步 → Demo
4. Phase 5（US3）→ 後端防護層完整，可抵擋繞過前端的請求 → Demo
5. Phase 6（Polish）→ Quickstart 驗收通過 → Release

### Parallel Team Strategy

1. 開發者 A + B 共同完成 Phase 1 + Phase 2
2. Phase 2 完成後：
   - 開發者 A：Phase 3（US1 前端）
   - 開發者 B：Phase 4 T007（US2 後端端點）+ Phase 5 T010（US3 Schema）
3. 各 Story 獨立完成後整合，互不阻擋

---

## Notes

- `[P]` 任務 = 不同檔案、無未完成依賴，可並行執行
- `[Story]` 標籤追蹤每個 Task 對應的 User Story，便於獨立驗收
- US1 可使用預設值 512 完整交付，無需等待 US2 後端 API 就緒
- US3 的 T010（`schemas/translation.py`）不影響現有 API 行為，可安全並行
- 字元計數以 Unicode code points 為單位（Python `len()` / C# `.Length` 對 BMP 字元一致，FR-009）
- `/api/config` 端點無需驗證（FR-010）；前端失敗時靜默回退 512，不阻擋操作（FR-011）
- `config.yaml` 無效值（≤ 0 或非整數）由 T003 強制覆寫為 512，服務不中斷（FR-008）
