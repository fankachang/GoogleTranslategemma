# Implementation Plan: TranslateGemma 網頁翻譯服務

**Branch**: `001-gemma-translate-web` | **Date**: 2026-02-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-gemma-translate-web/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

建立一個類似 ChatGPT 對話介面的網頁翻譯服務，包含前端單頁應用（Blazor WASM）和後端 API 服務（FastAPI），串接本地 TranslateGemma 模型（4B / 12B）進行多語言翻譯。核心功能包括自動語言偵測、逐 token 串流輸出、對話式介面、複製功能，以及雙層錯誤處理機制。系統無需帳號管理或持久化儲存，所有翻譯記錄保留於瀏覽器記憶體中。

## Technical Context

**Language/Version**: 
- 後端: Python 3.11+
- 前端: C# .NET 10 (Blazor WebAssembly)

**Primary Dependencies**:
- 後端: FastAPI, Hugging Face Transformers, PyYAML, uvicorn, torch
- 前端: Blazor WASM, MudBlazor, System.Net.Http

**Storage**: 無需持久化儲存 - 翻譯記錄僅保留於瀏覽器記憶體中（記憶體內狀態管理）

**Testing**: 
- 後端: pytest, pytest-asyncio
- 前端: bUnit, xUnit
- **測試策略**: TDD(測試驅動開發) - 先寫測試再實作功能，包含單元測試與整合測試
- **效能測試**: 初期忽略，先確保功能完整性

**Target Platform**: 
- 後端: Linux / macOS / Windows 伺服器，支援 Apple MPS、NVIDIA CUDA、CPU 推論
- 前端: 主流瀏覽器 (Chrome, Firefox, Safari, Edge) 最新版本

**Project Type**: Web application（前端 SPA + 後端 API）

**Performance Goals**: 
- 4B 模型：單次翻譯 ≤ 30 秒
- 12B 模型：單次翻譯 ≤ 60 秒
- 95% 正常請求（< 500 字元）在 20 秒內回傳第一個 token
- 串流輸出在 1 秒內開始顯示

**Constraints**: 
- 輸入文字上限：5000 字元
- 翻譯請求超時：120 秒
- 無狀態服務：不支援會話持久化
- 簡單為主：無帳號管理、無資料庫

**Scale/Scope**: 
- 單機部署、多人多電腦使用(預設 50 人以下)、無並發限制設計(依硬體資源決定)
- **僅支援繁體中文(zh-TW) <-> 英文(en)**，不支援簡體中文或其他語言
- 自動語言偵測僅支援繁體中文與英文
- 支援多瀏覽器分頁/視窗獨立翻譯記錄，屬於預設行為無需特殊處理
- 支援自訂術語對照表，允許使用者指定特定原文與譯文對應

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ✅ PASS (No constitution file exists for this project)

本專案尚未建立 constitution 檔案，無需進行合規性檢查。建議在專案成熟後建立 constitution，定義：
- 程式碼組織原則
- 測試策略與覆蓋率要求
- 依賴管理政策
- 效能與安全性基準

**Design Principles Applied** (基於規格要求)：
- ✅ **簡單為主**: 無帳號管理、無持久化、僅文字翻譯
- ✅ **前後端分離**: Blazor WASM 前端 + FastAPI 後端，透過 HTTP/SSE 通訊
- ✅ **無狀態設計**: 所有翻譯記錄存於瀏覽器記憶體，後端不保留會話
- ✅ **設定驅動**: 透過 `config.yaml` 切換模型與裝置，無需改程式碼
- ✅ **容器化部署**: 支援 Docker/Podman Compose 一鍵啟動

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend)
backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Load and validate config.yaml
│   ├── model.py             # TranslateGemma model loading & inference
│   ├── language_detect.py   # Auto language detection (中英文)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── translate.py     # POST /api/translate (with SSE streaming)
│   │   ├── languages.py     # GET /api/languages
│   │   └── health.py        # GET /health
│   └── schemas/
│       ├── __init__.py
│       ├── translation.py   # TranslationRequest, TranslationResponse
│       └── language.py      # Language model
├── tests/
│   ├── unit/
│   │   ├── test_config.py
│   │   ├── test_model.py
│   │   └── test_language_detect.py
│   ├── integration/
│   │   └── test_api_endpoints.py
│   └── conftest.py
├── requirements.txt
└── README.md

frontend/
├── Components/
│   ├── ChatBubble.razor     # 對話泡泡元件（原文右、譯文左）
│   ├── LanguageSelector.razor  # 語言選擇下拉選單
│   ├── TranslationInput.razor  # 文字輸入框（含字數限制）
│   └── ToastNotification.razor # Toast 通知元件
├── Pages/
│   └── Index.razor          # 主翻譯頁面
├── Services/
│   ├── ITranslationService.cs
│   ├── TranslationService.cs    # HttpClient 呼叫後端 API
│   └── LanguageDetectionService.cs # 前端語言偵測輔助
├── Models/
│   ├── TranslationRequest.cs
│   ├── TranslationResponse.cs
│   ├── Language.cs
│   └── TranslationHistory.cs  # 記憶體內歷史記錄
├── wwwroot/
│   ├── css/
│   └── index.html
├── Program.cs
├── _Imports.razor
├── frontend.csproj
└── README.md

# Deployment & Configuration
config.example.yaml          # 設定檔範例
config.yaml                  # 實際設定檔（gitignore）
docker-compose.yaml          # Podman/Docker Compose 定義
Containerfile                # 後端容器映像
.gitignore
README.md                    # 專案說明與快速開始```

**Structure Decision**: 採用 Web application 結構（Option 2），前端（Blazor WASM）與後端（FastAPI）分離部署。前端編譯為靜態檔案可由任何 HTTP 伺服器提供，後端 API 獨立運行。此結構符合前後端分離原則，便於獨立測試與部署。

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: N/A (No constitution violations to track)

本專案無 constitution 檔案，無違規需要記錄。設計遵循「簡單為主」原則，避免過度設計。

---

## 已產出文件

### Phase 0: Research & Technical Decisions
- ✅ **[research.md](./research.md)**: 11 項技術決策文件，涵蓋框架選擇、模型推論策略、錯誤處理、容器化、測試與優化策略
  - 前端框架: Blazor WASM vs React/Vue/Vanilla
  - 後端框架: FastAPI vs Flask/Node.js/Go
  - 模型推論: Transformers 直接載入 vs vLLM/TensorRT
  - 串流協定: SSE vs WebSocket
  - 語言偵測: Regex vs langdetect/fastText
  - 錯誤顯示: Toast + Dialog Bubble vs 純 Modal/純 Toast
  - 容器化: Podman/Docker 雙支援
  - 測試金字塔: Unit → Integration → E2E
  - 效能優化: 批次處理、KV cache、模型量化
  - 安全策略: 輸入驗證、Rate limiting、CORS
  - 未來功能: 批次翻譯、TTS、詞彙庫

### Phase 1: Data Model & Contracts
- ✅ **[data-model.md](./data-model.md)**: 6 個核心實體定義，含 Pydantic/C# schema
  - **TranslationRequest**: text (1-5000 字元), source_lang, target_lang, stream, glossary(術語對照表)
  - **TranslationResponse**: translation, source_lang, target_lang, detected 旗標
  - **Language**: code (ISO 639-1), name, native_name（僅支援 zh-TW 和 en）
  - **TranslationHistory**: 前端記憶體內歷史記錄（UUID, 來源/譯文, 時間戳記, 偵測旗標）
  - **HealthCheckResponse**: status (ok/degraded/error), model, device, model_loaded
  - **TerminologyGlossary**: 自訂術語對照表（source_text, target_text, source_lang, target_lang, case_sensitive）
  - 驗證規則: 前端即時驗證 + 後端 FastAPI Pydantic 驗證
  - 狀態轉換: Created → Validating → Sending → Streaming → Completed
  - 錯誤模型: 6 種常見錯誤類型（validation_error, timeout, model_not_loaded 等）

- ✅ **[contracts/openapi.yaml](./contracts/openapi.yaml)**: OpenAPI 3.0 規格
  - **POST /api/translate**: 文字翻譯（支援 JSON 或 SSE 串流回應）
  - **GET /api/languages**: 支援語言清單
  - **GET /health**: 服務健康檢查
  - 完整 schema 定義、錯誤回應範例、SSE 串流格式文件

- ✅ **[quickstart.md](./quickstart.md)**: 快速入門指南
  - 環境需求（Python 3.11+, .NET 10, GPU/CPU 配置）
  - 本地開發流程（模型下載、設定檔建立、後端/前端啟動）
  - Docker Compose 一鍵部署
  - 安裝驗證（健康檢查、翻譯測試、UI 測試）
  - 常見問題排除（模型載入失敗、CUDA OOM、逾時、CORS、白畫面）
  - 效能基準（4B/12B 模型在不同硬體的表現）

---

## 下階段計畫

### Phase 2: Task Breakdown (由 `/speckit.tasks` 命令生成)

規劃細部實作任務：
1. **任務粒度**: 3-7 小時可完成的開發單元
2. **依賴關係**: 任務間的先後順序與依賴
3. **驗收標準**: 每個任務的 Definition of Done
4. **測試策略**: 單元測試、整合測試、E2E 測試分配

預期產出：`tasks.md` 包含所有可執行任務清單。

### Phase 3: Implementation

基於 `tasks.md` 開始實作：
- 後端 API 端點實作
- 前端 UI 元件開發
- 測試案例撰寫
- 整合測試驗證
- 效能調校與優化
- 文件完善與範例程式碼

---

## 參考文件導覽

- **功能規格**: [spec.md](./spec.md) - 17 項功能需求與 9 項驗收標準
- **需求檢核表**: [checklists/requirements.md](./checklists/requirements.md) - 規格品質驗證
- **技術決策**: [research.md](./research.md) - 為何選擇 Blazor + FastAPI + Transformers
- **資料模型**: [data-model.md](./data-model.md) - API 實體定義與驗證規則
- **API 契約**: [contracts/openapi.yaml](./contracts/openapi.yaml) - RESTful API 完整規格
- **快速入門**: [quickstart.md](./quickstart.md) - 從零到運行的完整步驟
