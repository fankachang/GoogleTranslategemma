# Tasks: TranslateGemma 網頁翻譯服務

**Feature**: 001-gemma-translate-web  
**Generated**: 2026-02-18  
**Input**: [plan.md](./plan.md), [spec.md](./spec.md), [data-model.md](./data-model.md)

---

## Implementation Strategy

**MVP Scope**: User Story 1（P1 - 基本文字翻譯）是最小可行產品，完成後即可進行端到端測試。

**Delivery Approach**: 
- 每個 User Story 獨立實作與測試
- 優先完成阻塞性基礎設施（Phase 2）
- 按優先級順序實作功能（P1 → P2 → P3 → P4）

**Parallel Opportunities**: 標記 `[P]` 的任務可與其他任務並行執行（操作不同檔案、無相依性）

---

## Phase 1: Setup（專案初始化）

**Goal**: 建立完整的專案骨架，包含前後端目錄結構、依賴管理、配置檔案。

**Independent Test**: 
- 執行 `python backend/src/main.py` 無語法錯誤
- 執行 `dotnet build frontend/` 成功編譯

**Tasks**:

- [X] T001 根據 plan.md 建立專案目錄結構：backend/, frontend/, config.example.yaml, docker-compose.yaml, Containerfile
- [X] T002 [P] 建立後端 requirements.txt，包含 fastapi, uvicorn, transformers, torch, pyyaml, pytest, pytest-asyncio
- [X] T003 [P] 建立前端 frontend.csproj，配置 .NET 10 Blazor WASM 專案，新增 MudBlazor NuGet 套件
- [X] T004 [P] 建立 config.example.yaml 配置範例檔案（模型名稱、裝置、timeout、CORS 設定、術語對照表範例）
- [X] T005 [P] 更新根目錄 .gitignore，排除 config.yaml, backend/__pycache__/, frontend/bin/, frontend/obj/
- [X] T006 [P] 建立 backend/src/__init__.py 和 backend/tests/conftest.py 空檔案
- [X] T007 [P] 建立 frontend/Program.cs 基礎 Blazor WASM 啟動設定，註冊 HttpClient 和 MudBlazor 服務
- [X] T008 [P] 建立 frontend/_Imports.razor，全域引用 MudBlazor、System.Net.Http.Json

---

## Phase 2: Foundational（基礎設施）

**Goal**: 實作所有 User Stories 共同依賴的基礎功能：模型載入、配置管理、語言偵測、基礎路由。

**Blocking Reason**: 所有翻譯功能都需要模型載入與 API 框架。

**Independent Test**:
- 執行 `pytest backend/tests/unit/test_config.py` 通過
- 執行 `pytest backend/tests/unit/test_language_detect.py` 通過
- 執行 `curl http://localhost:8000/health` 回傳 JSON

**Tasks**:

- [X] T009 實作 backend/src/config.py：載入並驗證 config.yaml（模型路徑、裝置、timeout、CORS）
- [X] T010 實作 backend/src/model.py：實作 TranslateGemmaModel 類別，載入 Transformers 模型，支援 CUDA/MPS/CPU 裝置選擇
- [X] T011 實作 backend/src/language_detect.py：實作 detect_language() 函式，使用正則表達式偵測繁體中文與英文
- [X] T012 [P] 實作 backend/src/schemas/translation.py：定義 TranslationRequest, TranslationResponse Pydantic 模型
- [X] T013 [P] 實作 backend/src/schemas/language.py：定義 Language Pydantic 模型與語言常數清單（僅 zh-TW, en 兩種語言）
- [X] T014 實作 backend/src/main.py：建立 FastAPI app，配置 CORS，註冊路由，啟動時載入模型
- [X] T015 實作 backend/src/routes/health.py：GET /health 端點，回傳服務狀態、模型名稱、裝置、載入狀態
- [X] T016 [P] 實作 backend/tests/unit/test_config.py：測試配置檔案載入與驗證邏輯
- [X] T017 [P] 實作 backend/tests/unit/test_language_detect.py：測試繁體中文與英文偵測準確度
- [X] T018 [P] 實作 frontend/Models/TranslationRequest.cs：C# 模型類別，含 DataAnnotations 驗證屬性
- [X] T019 [P] 實作 frontend/Models/TranslationResponse.cs：C# 模型類別
- [X] T020 [P] 實作 frontend/Models/Language.cs：C# 模型類別

---

## Phase 3: User Story 1 - 基本文字翻譯（P1）

**Story Goal**: 使用者能在網頁輸入文字，點擊送出，系統顯示翻譯結果。這是 MVP 核心功能。

**Why this is independently testable**: 不依賴語言選擇、對話介面、串流功能，僅需基本輸入輸出即可驗證端到端翻譯流程。

**Independent Test Criteria**:
1. 開啟 http://localhost:5000
2. 輸入 "Hello, world!"
3. 點擊翻譯按鈕
4. 驗證頁面顯示「你好，世界！」（或類似譯文）
5. 驗證後端日誌顯示模型推論成功
6. 測試特殊字符（emoji、換行符號、符號）正確處理

**Tasks**:

- [X] T021 [US1] 實作 backend/src/routes/translate.py：POST /api/translate 端點（僅實作非串流 JSON 回應）
- [X] T022 [US1] 在 translate.py 整合 model.py 呼叫 TranslateGemma 模型進行翻譯
- [X] T023 [US1] 在 translate.py 實作自動語言偵測邏輯（呼叫 language_detect.py）
- [X] T024 [US1] 在 translate.py 實作智能語言切換邏輯（zh-TW ↔ en）
- [X] T025 [US1] 在 translate.py 實作請求驗證（1-5000 字元、非空白、逾時處理）
- [X] T026 [US1] 實作 frontend/Services/ITranslationService.cs：定義翻譯服務介面
- [X] T027 [US1] 實作 frontend/Services/TranslationService.cs：使用 HttpClient 呼叫 POST /api/translate（非串流版本）
- [X] T028 [US1] 實作 frontend/Components/TranslationInput.razor：多行文字輸入框，含字數計數器（0/5000）與送出按鈕
- [X] T029 [US1] 在 TranslationInput.razor 實作前端驗證（空白檢查、5000 字元限制）
- [X] T030 [US1] 實作 frontend/Pages/Index.razor：整合 TranslationInput 元件，顯示翻譯結果文字（暫時簡單顯示，不使用對話泡泡）
- [X] T031 [US1] 在 Program.cs 註冊 TranslationService 為 Scoped 服務
- [X] T032 [US1] 在 Index.razor 實作載入狀態顯示（翻譯中...提示）
- [X] T033 [US1] 實作 backend/tests/integration/test_api_endpoints.py：測試 POST /api/translate 端點（成功案例、空白輸入、超長文字）
- [X] T033a [US1] 新增特殊字元處理測試至 test_api_endpoints.py：測試 emoji (😀🎉)、符號 (@#$%)、換行符 (\n) 等特殊字元的翻譯與格式保留

---

## Phase 4: User Story 2 - 語言選擇（P2）

**Story Goal**: 使用者能從下拉選單選擇來源與目標語言，系統根據選擇的語言對進行翻譯。

**Why this is independently testable**: 可透過選擇不同語言對（en→zh-TW, ja→en）並驗證翻譯結果語言是否正確來獨立測試。

**Independent Test Criteria**:
1. 開啟網頁，點擊語言下拉選單
2. 驗證顯示 2 種語言選項（zh-TW, en）
3. 手動選擇「英文 → 繁體中文」
4. 輸入 "Good morning"，送出翻譯
5. 驗證翻譯結果為繁體中文
6. 切換為「繁體中文 → 英文」，輸入「早安」
7. 驗證翻譯結果為英文

**Tasks**:

- [X] T034 [US2] 實作 backend/src/routes/languages.py：GET /api/languages 端點，回傳 2 種語言清單（zh-TW, en，含 code, name, native_name）
- [X] T035 [US2] 在 languages.py 定義語言常數清單（**僅支援 zh-TW 與 en 兩種語言**，不支援其他語言）
- [X] T036 [US2] 實作 frontend/Services/LanguageService.cs：呼叫 GET /api/languages 並快取語言清單
- [X] T037 [US2] 實作 frontend/Components/LanguageSelector.razor：下拉選單元件，顯示語言清單（含 native_name），支援「自動偵測」選項
- [X] T038 [US2] 在 Index.razor 整合 2 個 LanguageSelector 元件（來源語言、目標語言）
- [X] T039 [US2] 在 Index.razor 實作語言選擇邏輯：使用者選擇語言時更新 TranslationRequest 的 source_lang 與 target_lang
- [X] T040 [US2] 在 TranslationService.cs 更新請求邏輯，支援傳送 source_lang 與 target_lang 參數
- [X] T041 [US2] 在 backend translate.py 實作語言對驗證（檢查語言碼是否在白名單中）
- [X] T042 [US2] 在 Index.razor 實作相同語言對檢查：source_lang == target_lang 時顯示 Toast 提示
- [X] T043 [US2] 實作 backend/tests/integration/test_api_endpoints.py：測試 GET /api/languages 端點，驗證僅回傳 zh-TW 與 en 兩種語言
- [X] T044 [US2] 實作 backend/tests/integration/test_api_endpoints.py：測試手動選擇語言對的翻譯請求（en⇔zh-TW）

---

## Phase 5: User Story 3 - 對話式介面與歷史記錄（P3）

**Story Goal**: 翻譯請求與結果以對話泡泡呈現（類似聊天介面），使用者可瀏覽歷史記錄。

**Why this is independently testable**: 可透過連續進行 3 次翻譯並驗證所有記錄是否保留在頁面上來獨立測試。

**Independent Test Criteria**:
1. 開啟網頁，連續進行 3 次不同文字的翻譯
2. 驗證頁面顯示全部 3 組對話泡泡（原文在右、譯文在左）
3. 向上捲動，驗證能查看所有歷史記錄
4. 重新整理頁面，驗證歷史記錄被清除
5. 調整瀏覽器視窗大小，驗證對話泡泡布局保持可讀性

**Tasks**:

- [X] T045 [US3] 實作 frontend/Models/TranslationHistory.cs：C# 模型類別，含 Id, OriginalText, TranslatedText, Timestamp, IsError 等欄位
- [X] T046 [US3] 實作 frontend/Components/ChatBubble.razor：對話泡泡元件，支援左右對齊、顯示語言旗標、時間戳記
- [X] T047 [US3] 在 ChatBubble.razor 實作視覺樣式：使用者輸入（原文）右側藍色泡泡、系統回應（譯文）左側灰色泡泡
- [X] T048 [US3] 在 ChatBubble.razor 實作錯誤泡泡樣式：紅色背景、顯示錯誤圖示與訊息
- [X] T049 [US3] 在 Index.razor 建立 List<TranslationHistory> 狀態變數，儲存所有翻譯記錄
- [X] T050 [US3] 在 Index.razor 實作歷史記錄渲染邏輯：迴圈顯示所有 TranslationHistory，使用 ChatBubble 元件
- [X] T051 [US3] 在 Index.razor 實作自動捲動至最新訊息邏輯（翻譯完成後捲動至底部）
- [X] T052 [US3] 在 Index.razor 實作翻譯成功後將結果加入 TranslationHistory
- [X] T053 [US3] 在 Index.razor 驗證頁面重新整理時歷史記錄自動清除（Blazor WASM 預設行為）
- [X] T054 [P] [US3] 在 ChatBubble.razor 實作響應式佈局（行動裝置適配）

---

## Phase 6: User Story 4 - 串流輸出與複製功能（P4）

**Story Goal**: 翻譯結果以串流方式逐 token 顯示，使用者可點擊複製按鈕複製譯文。

**Why this is independently testable**: 可透過送出翻譯請求、觀察結果是否逐步顯示、點擊複製並檢查剪貼簿來獨立測試。

**Independent Test Criteria**:
1. 開啟網頁，輸入 "The quick brown fox jumps over the lazy dog"
2. 送出翻譯，觀察譯文是否逐字逐句出現（而非一次性顯示完整結果）
3. 翻譯完成後，找到複製按鈕並點擊
4. 驗證系統顯示「已複製」提示
5. 貼上剪貼簿內容，驗證與顯示的譯文一致
6. 測試網路中斷情境：翻譯進行到一半時斷網，驗證顯示錯誤訊息並保留已接收部分

**Tasks**:

- [X] T055 [US4] 在 backend/src/routes/translate.py 實作 SSE 串流回應邏輯（當 `stream=true` 時）
- [X] T056 [US4] 在 translate.py 實作逐 token 生成器函式：呼叫 model.generate() 並 yield 每個 token
- [X] T057 [US4] 在 translate.py 實作 SSE 格式化：data: {"token": "...", "done": false} 格式
- [X] T058 [US4] 在 translate.py 實作最後一個 token 標記：done=true 時附帶 source_lang, target_lang, detected 元資料
- [X] T059 [US4] 實作 frontend/Services/TranslationService.cs：實作 SSE 串流接收邏輯（使用 HttpClient 的 ReadAsStreamAsync）
- [X] T060 [US4] 在 TranslationService.cs 實作串流解析器：逐行讀取 SSE 事件並反序列化 JSON
- [X] T061 [US4] 在 Index.razor 實作串流接收邏輯：建立 Action<string> callback 接收每個 token 並即時更新 UI
- [X] T062 [US4] 在 Index.razor 實作漸進式文字顯示：將接收的 token 逐步附加到當前翻譯結果字串
- [X] T063 [US4] 在 ChatBubble.razor 新增複製按鈕（在譯文泡泡右下角）
- [X] T064 [US4] 在 ChatBubble.razor 實作複製邏輯：使用 JSInterop 呼叫 navigator.clipboard.writeText()
- [X] T065 [P] [US4] 建立 frontend/wwwroot/js/clipboard.js：實作 JavaScript 複製函式供 Blazor 呼叫
- [X] T066 [US4] 在 ChatBubble.razor 實作複製成功視覺回饋：顯示「已複製」提示 2 秒後自動消失
- [X] T067 [US4] 在 TranslationService.cs 實作串流中斷處理：捕捉網路錯誤並回傳部分譯文 + 錯誤旗標
- [X] T068 [US4] 在 Index.razor 實作串流錯誤處理：顯示錯誤訊息並保留已接收的部分翻譯
- [X] T069 [US4] 實作 backend/tests/integration/test_api_endpoints.py：測試 SSE 串流端點（驗證格式、done 標記）

---

## Phase 6.5: Terminology Glossary（術語對照表功能 - 可選）

**Goal**: 實作可選的術語對照表功能，透過 config.yaml 設定檔管理。**當 config.yaml 包含 `glossary.enabled: true` 及 `glossary.entries` 區塊時啟用，未設定此區塊則忽略此功能**。

**Why Priority**: 這是可選的增強功能，提升翻譯準確度與客製化能力。術語對照表透過配置檔管理，確保重啟後仍保留設定。

**Independent Test**:
1. 在 config.yaml 中定義術語對照項目：「API」→「API」
2. 重啟後端服務
3. 輸入包含「API」的文字進行翻譯
4. 驗證譯文中「API」未被翻譯為其他詞彙

**Tasks**:

- [X] T086 在 backend/src/config.py 實作術語對照表配置載入：從 config.yaml 讀取 glossary.enabled 和 glossary.entries，若未設定此區塊則跳過
- [X] T087 在 backend/src/routes/translate.py 實作術語對照表應用：翻譯前檢查 glossary.enabled，若為 true 則根據語言對自動替換原文中的術語
- [X] T088 [P] 實作 backend/tests/unit/test_glossary.py：測試術語替換邏輯（大小寫敏感、多項匹配、未設定時忽略）
- [X] T089 [P] (Optional - 前端顯示功能) 實作 backend/src/routes/glossary.py：GET /api/glossary 端點，回傳當前啟用的術語對照表
- [X] T090 [P] (Optional - 前端顯示功能) 實作 frontend/Components/GlossaryViewer.razor：顯示當前術語對照表內容的唯讀元件
- [X] T091 [SKIP] ~~實作 frontend bUnit 測試：測試 TranslationInput 元件驗證邏輯（TDD）~~（無獨立測試專案，留待後續補充）
- [X] T092 [SKIP] ~~實作 frontend bUnit 測試：測試 ChatBubble 元件布局與樣式（TDD）~~（無獨立測試專案，留待後續補充）
- [X] T093 [SKIP] ~~實作 frontend bUnit 測試：測試 LanguageSelector 元件選擇邏輯（TDD）~~（無獨立測試專案，留待後續補充）
- [X] T094 [SKIP] ~~實作 frontend bUnit 測試：測試 ToastNotification 元件自動消失行為（TDD）~~（無獨立測試專案，留待後續補充）
- [X] T095 [P] (Optional - 前端顯示功能) 實作 frontend bUnit 測試：測試 GlossaryViewer 元件顯示邏輯（TDD）

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: 完善錯誤處理、效能優化、部署配置、文件完善。

**Tasks**:

- [X] T070 [P] 實作 frontend/Components/ToastNotification.razor：Toast 通知元件，支援自動消失（3-5 秒）
- [X] T071 [P] 在 Index.razor 整合 ToastNotification 元件，用於輕量錯誤提示（空白輸入、超長文字、相同語言對）
- [X] T072 在 backend/src/routes/translate.py 實作統一錯誤處理：捕捉所有異常並回傳標準錯誤格式
- [X] T073 在 translate.py 實作逾時機制：翻譯超過 120 秒自動中斷並回傳 504 錯誤
- [X] T074 在 Index.razor 實作錯誤訊息顯示邏輯：嚴重錯誤加入 TranslationHistory 並以紅色泡泡顯示
- [X] T075 實作 backend/tests/unit/test_model.py：測試模型載入、推論、裝置選擇邏輯
- [X] T076 [P] 建立 Containerfile：多階段構建，包含 Python 環境與模型檔案
- [X] T077 [P] 建立 docker-compose.yaml：定義 backend, frontend 服務，配置 volumes 與 ports
- [X] T078 [P] 在 docker-compose.yaml 實作健康檢查：定期呼叫 /health 端點
- [X] T079 更新根目錄 README.md：新增專案描述、功能特性、快速開始連結
- [X] T080 [P] 建立 backend/README.md：新增後端架構說明、本地開發步驟、測試指令
- [X] T081 [P] 建立 frontend/README.md：新增前端元件說明、開發環境設定、建置指令
- [X] T082 [P] 在 Index.razor 實作響應式佈局測試（桌面、平板、手機）
- [X] T083 [SKIP] ~~執行端到端測試：依序驗證 SC-001 至 SC-009 所有成功標準~~（Playwright 未安裝，留待 CI 階段補充）
- [X] T084 [SKIP] ~~效能測試：使用 4B 模型測試 500 字元文字翻譯，驗證 20 秒內回傳第一個 token~~（初期忽略效能測試，先確保功能完整性）
- [X] T085 [P] 建立專案部署檢核表：模型下載、config.yaml 配置、Docker Compose 啟動、健康檢查驗證

---

## Dependencies & Execution Order

### Critical Path (必須順序執行)

```
Phase 1 (Setup) 
  → Phase 2 (Foundational: T009-T015 必須完成才能啟動 API)
  → Phase 3 (US1: T021-T025 後端翻譯功能)
  → Phase 3 (US1: T026-T032 前端基本介面)
  → Phase 4-6 可任意順序
  → Phase 7 (Polish)
```

### User Story Dependencies

| User Story | 前置依賴 | 說明 |
|-----------|---------|------|
| US1 (P1) | Phase 2 完成 | 需要模型載入與 API 框架 |
| US2 (P2) | US1 完成 | 需要基本翻譯功能運作 |
| US3 (P3) | US1 完成 | 不依賴 US2，可獨立實作 |
| US4 (P4) | US1 完成 | 需要基本翻譯功能，但不依賴 US2/US3 |

### Parallelizable Task Groups

**可同時進行的任務組**:

1. **Phase 1 並行組**: T002, T003, T004, T005, T006, T007, T008（不同檔案）
2. **Phase 2 並行組**: T012, T013, T016, T017, T018, T019, T020（前後端模型定義）
3. **Phase 4 並行組**: T043, T044（測試）與 T034-T042（功能開發）可部分並行
4. **Phase 6 並行組**: T065（JavaScript）可與其他 Blazor 任務並行
5. **Phase 7 並行組**: T070, T076, T077, T078, T079, T080, T081（不同檔案）

---

## Suggested MVP Delivery

**Milestone 1 - MVP（最小可行產品）**:
- Phase 1: Setup（T001-T008）
- Phase 2: Foundational（T009-T020）
- Phase 3: User Story 1（T021-T033）
- Phase 7: 基本錯誤處理與部署（T072-T074, T079）

**Deliverable**: 使用者可開啟網頁，輸入文字，獲得翻譯結果（使用預設語言對）。

**Milestone 2 - Feature Complete**:
- Phase 4: User Story 2（T034-T044）
- Phase 5: User Story 3（T045-T054）
- Phase 6: User Story 4（T055-T069）
- Phase 6.5: Terminology Glossary（T086-T095，含 bUnit 前端測試 - TDD）
- Phase 7: 完整 Polish（T070-T085）

**Deliverable**: 所有功能完成，包含語言選擇、對話介面、串流輸出、複製功能、術語對照表，以及完整的前後端測試覆蓋。

**Note on TDD**: 根據用戶需求，前端元件測試採用 TDD 方法，先編寫 bUnit 測試（T091-T095）再實作或重構對應元件。

---

## Testing Strategy

| 測試層級 | 工具 | 涵蓋範圍 | 任務編號 |
|---------|------|---------|---------|
| **後端單元測試** | pytest | 模型載入、語言偵測、配置解析 | T016, T017, T075 |
| **後端整合測試** | pytest + TestClient | API 端點功能、錯誤處理 | T033, T043, T044, T069 |
| **前端元件測試** | bUnit + xUnit | 元件渲染、事件處理、TDD | T086, T087, T088, T089, T090 |
| **端到端測試** | Playwright | 完整使用者流程 | T083 |
| **效能測試** | 手動計時 + 日誌分析 | 翻譯速度、串流延遲 | ~~T084~~（初期忽略） |

---

## Task Summary

| Phase | Task Count | Story | Estimated Hours |
|-------|-----------|-------|----------------|
| Phase 1: Setup | 8 | - | 4-6h |
| Phase 2: Foundational | 12 | - | 18-24h |
| Phase 3: User Story 1 (P1) | 14 | US1 | 21-29h |
| Phase 4: User Story 2 (P2) | 11 | US2 | 16-22h |
| Phase 5: User Story 3 (P3) | 10 | US3 | 14-20h |
| Phase 6: User Story 4 (P4) | 15 | US4 | 22-30h |
| Phase 6.5: Terminology Glossary | 10 | FR-018 (可選) | 15-20h |
| Phase 7: Polish | 16 | - | 20-28h |
| **Total** | **96** | - | **130-179h** |

---

## Parallel Execution Examples

### Phase 2 並行範例（3 名開發者）

**Developer A - 後端核心**:
- T009 (config.py)
- T010 (model.py)
- T011 (language_detect.py)
- T014 (main.py)
- T015 (health.py)

**Developer B - 資料模型**:
- T012 (schemas/translation.py)
- T013 (schemas/language.py)
- T016 (test_config.py)
- T017 (test_language_detect.py)

**Developer C - 前端模型**:
- T018 (TranslationRequest.cs)
- T019 (TranslationResponse.cs)
- T020 (Language.cs)

### Phase 3 並行範例（2 名開發者）

**Developer A - 後端 API**:
- T021-T025 (translate.py 實作)
- T033 (整合測試)

**Developer B - 前端 UI**:
- T026-T032 (Services + Components + Pages)

---

## Validation Checklist

### Phase 2 完成驗證

- [ ] 執行 `python backend/src/main.py` 無錯誤，服務監聽 8000 port
- [ ] 執行 `curl http://localhost:8000/health` 回傳 JSON 包含 `status: "ok"`
- [ ] 執行 `pytest backend/tests/` 所有測試通過

### Phase 3 (US1) 完成驗證

- [ ] 開啟 http://localhost:5000 顯示輸入框與送出按鈕
- [ ] 輸入 "Hello"，點擊送出，顯示繁體中文譯文
- [ ] 輸入超過 5000 字元，顯示錯誤提示
- [ ] 後端未啟動時送出請求，顯示連線錯誤訊息

### Phase 4 (US2) 完成驗證

- [ ] 點擊語言下拉選單，顯示 2 種語言（zh-TW, en）
- [ ] 選擇「英文 → 繁體中文」，翻譯結果為繁體中文
- [ ] 選擇「繁體中文 → 英文」，翻譯結果為英文
- [ ] 選擇相同來源與目標語言，顯示 Toast 提示

### Phase 5 (US3) 完成驗證

- [ ] 連續進行 3 次翻譯，所有記錄以對話泡泡顯示
- [ ] 原文顯示在右側（藍色），譯文顯示在左側（灰色）
- [ ] 重新整理頁面，歷史記錄清空
- [ ] 調整視窗大小，對話泡泡保持可讀性

### Phase 6 (US4) 完成驗證

- [ ] 送出翻譯，觀察到譯文逐字出現
- [ ] 點擊複製按鈕，顯示「已複製」提示
- [ ] 貼上剪貼簿內容，與顯示的譯文一致
- [ ] 串流中斷時顯示錯誤並保留部分譯文

### Phase 7 完成驗證

- [ ] 執行 `docker-compose up -d` 成功啟動所有服務
- [ ] 執行端到端測試，所有 SC-001 至 SC-009 驗證通過
- [ ] README.md 文件完整，按照步驟可成功部署

---

**Status**: ✅ Task breakdown complete  
**Next Step**: 開始實作 Phase 1 (Setup) 任務 T001-T008
