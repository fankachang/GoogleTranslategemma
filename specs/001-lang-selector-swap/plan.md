# Implementation Plan: 語系選擇器與互換功能

**Branch**: `001-lang-selector-swap` | **Date**: 2026-04-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-lang-selector-swap/spec.md`

## Summary

在現有 Blazor WebAssembly + FastAPI 架構上，新增語系選擇器功能：

1. **後端**：擴充 `GET /api/config` 回傳 `features.language_selector` 旗標；在 `config.yaml` 新增 `features` 區塊。
2. **前端**：在 `Index.razor` 整合既有 `LanguageSelector.razor` 元件，顯示「原語系 ↔ 目的語系」列；實作互換按鈕、FR-009 自動切換邏輯、載入中停用狀態，以及相同語系 inline 警告。功能的顯示與否由 `GET /api/config` 控制，失敗時回退隱藏。

## Technical Context

**Language/Version**: Python 3.13（後端）、.NET 9 Blazor WebAssembly（前端）  
**Primary Dependencies**: FastAPI、Pydantic v2（後端）；MudBlazor、HttpClient（前端）  
**Storage**: N/A（無持久化儲存）  
**Testing**: pytest（後端單元 + 整合測試）；dotnet test（前端）  
**Target Platform**: Linux server（後端容器）+ 瀏覽器 WASM（前端）  
**Project Type**: Web application（Blazor WASM ↔ FastAPI）  
**Performance Goals**: 語系切換 UI 反應時間 < 200ms；FR-009 自動切換 < 100ms  
**Constraints**: 不可硬寫旗標於前端程式碼；config 載入失敗不中斷翻譯主功能  
**Scale/Scope**: 小功能，僅 2 種語系（zh-TW, en），無分頁或持久化需求

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 評估 | 狀態 |
|---|---|---|
| I. Localization-First | 規格、計畫、程式碼註解均使用 zh-TW；constitution 本身為英文 | ✅ PASS |
| II. API Contract Integrity | `GET /api/config` 後端已存在，需擴充回傳欄位；`GET /api/languages` 後端已存在；所有呼叫先驗證後端實作 | ✅ PASS |
| III. Simplicity & YAGNI | 僅整合既有元件（`LanguageSelector.razor`、`LanguageService.cs`），新增最小量程式碼；無多餘抽象 | ✅ PASS |
| IV. Test-First Development | 計畫需包含測試策略，實作前先寫失敗測試 | ✅ REQUIRED — tasks.md 需包含測試任務 |
| V. UI Layout Consistency | 語系選擇器列放置於輸入區上方，與現有佈局 `ContentWidthPercent` 對齊 | ✅ PASS |
| VI. Virtual Environment Hygiene | 後端使用現有 `.venv`，不建立新環境 | ✅ PASS |
| VII. Observability & Debuggability | 前端 config/languages 載入失敗時需 console.error；後端 `GET /api/config` 豁免額外結構化 logging（理由：純靜態設定讀取，無副作用，FastAPI middleware 已涵蓋請求層級 logging，個別 endpoint logging 不增加可觀察性價值） | ✅ PASS |

**Constitution Check 結論：PASS — 無違規，可進入 Phase 0**

## Project Structure

### Documentation (this feature)

```text
specs/001-lang-selector-swap/
├── plan.md              # 本檔案
├── research.md          # Phase 0 產出
├── data-model.md        # Phase 1 產出
├── quickstart.md        # Phase 1 產出
├── contracts/           # Phase 1 產出
│   ├── api-config.md
│   └── api-languages.md
└── tasks.md             # Phase 2 產出（/speckit.tasks 指令）
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── config.py              # 擴充：新增 features 區塊 setdefault
│   ├── routes/
│   │   └── config.py          # 擴充：回傳 features.language_selector
│   └── schemas/
│       └── language.py        # 無異動（已有 Language schema）
└── tests/
    ├── unit/
    │   └── test_config_features.py   # 新增
    └── integration/
        └── test_api_config.py        # 新增（驗證回傳欄位）

frontend/
├── AppConfig.cs               # 擴充：新增 LanguageSelectorEnabled bool
├── Models/
│   └── AppConfigResponse.cs   # 擴充：新增 LanguageSelectorEnabled
├── Pages/
│   └── Index.razor            # 擴充：整合語系選擇器列
├── Components/
│   └── LanguageSelector.razor # 無異動（已完整）
└── Services/
    └── LanguageService.cs     # 無異動（已完整）

config.yaml                    # 擴充：新增 features.language_selector
config.example.yaml            # 擴充：新增 features.language_selector（含說明）
```

**Structure Decision**: Web application（Option 2）。前後端分離，後端修改集中在 `config.py` 與 `routes/config.py`；前端修改集中在 `Index.razor` 與 `AppConfig.cs`/`AppConfigResponse.cs`。

## Phase 0 產出

- [research.md](./research.md) — 7 個研究問題全部解決，無殘留 NEEDS CLARIFICATION

## Phase 1 設計成果

| 文件 | 說明 |
|---|---|
| [data-model.md](./data-model.md) | 實體定義（Language、FeaturesConfig、AppConfigResponse、AppConfig）；FR-009 狀態機；驗證規則 |
| [contracts/api-config.md](./contracts/api-config.md) | `GET /api/config` 擴充合約（新增 `features.language_selector`） |
| [contracts/api-languages.md](./contracts/api-languages.md) | `GET /api/languages` 現有合約確認（無異動） |
| [quickstart.md](./quickstart.md) | 開發者快速上手：config.yaml 設定 → 後端修改 → 前端修改 → 驗證步驟 |

## Phase 1 後 Constitution Check

| 原則 | Phase 1 後評估 | 狀態 |
|---|---|---|
| I. Localization-First | data-model.md / contracts / quickstart 均以 zh-TW 撰寫；API 欄位名稱為英文（技術規範） | ✅ PASS |
| II. API Contract Integrity | `GET /api/config` 合約明確定義擴充欄位；`GET /api/languages` 確認無異動；前端 DTO 與後端回傳精確對應 | ✅ PASS |
| III. Simplicity & YAGNI | `FeaturesConfig` 僅含 1 欄位；`AppConfigResponse` 轉換為 init-only properties 是必要的技術調整，非過度設計 | ✅ PASS |
| IV. Test-First Development | `test_config_features.py` 與 `test_api_config.py` 已列為 Project Structure 的新增檔案；tasks.md 需確保測試任務排在實作之前 | ✅ REQUIRED — tasks.md 須遵守 |
| V. UI Layout Consistency | quickstart.md 明確定義語系列寬度與 `ContentWidthPercent` 一致，位於 `<TranslationInput>` 上方 | ✅ PASS |
| VI. Virtual Environment Hygiene | 後端無新增依賴套件，不影響 `.venv` | ✅ PASS |
| VII. Observability & Debuggability | contracts/api-config.md 定義失敗時前端回退行為；`console.error` 記錄 config/languages 失敗需在 tasks.md 中明確列出 | ✅ PASS |

**Phase 1 後 Constitution Check 結論：PASS — 設計符合所有原則，可進入 Phase 2（tasks.md 生成）**

## Complexity Tracking

> 無 Constitution 違規，此區塊不需填寫。
