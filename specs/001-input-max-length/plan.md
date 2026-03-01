# Implementation Plan: 可設定的翻譯輸入字數上限

**Branch**: `001-input-max-length` | **Date**: 2026-03-01 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-input-max-length/spec.md`

## Summary

在前後端加入可透過 `config.yaml` 設定的翻譯輸入字數上限功能，預設值 512 字元。  
後端新增 `GET /api/config` 端點供前端讀取上限值（FR-006 單一設定來源），並在 `POST /api/translate` 中以 HTTP 422 拒絕超限請求；前端於初始化時取得上限後即時更新字數計數器、超限停用送出按鈕，並顯示友善的後端錯誤訊息。

## Technical Context

**Language/Version**: Python 3.11（後端）、C# 9 / .NET 8 Blazor WASM（前端）  
**Primary Dependencies**: FastAPI + Pydantic v2（後端）；MudBlazor、Microsoft.AspNetCore.Components.WebAssembly（前端）  
**Storage**: N/A（設定僅讀自 `config.yaml`，無資料庫）  
**Testing**: pytest（後端 `backend/tests/`）；無前端自動化測試框架（目前無 bUnit 等設置）  
**Target Platform**: Linux 容器（後端）；瀏覽器 WASM（前端）  
**Project Type**: Web application（backend + frontend 分離）  
**Performance Goals**: 字數計數更新 ≤ 100 ms（SC-001）；送出按鈕停用 ≤ 100 ms（SC-002）  
**Constraints**: `/api/config` 無需驗證（FR-010）；`/api/config` 失敗時前端靜默回退預設值 512（FR-011）；字元計數以 Unicode code points 為單位（FR-009）；有效上限範圍 1–10,000（SC-005）  
**Scale/Scope**: 單人使用 / 小型部署；本次僅影響 2 後端路由 + 3 前端元件 + 2 設定檔

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| 無新增第三方依賴 | ✅ PASS | 完全使用既有 FastAPI / MudBlazor；無新套件 |
| 單一設定來源 | ✅ PASS | 前後端均從 `config.yaml` → `app.state.config` → `/api/config` 取得上限值（FR-006） |
| 公開端點安全 | ✅ PASS | `/api/config` 僅回傳非敏感設定值（`max_input_length`），無需驗證符合 FR-010 |
| 向下相容 | ✅ PASS | `config.yaml` 若缺少欄位時系統回退預設值 512，服務不中斷（FR-008） |
| schema 上限合理 | ✅ PASS | `TranslationRequest.text` 改 `max_length=10000` 作為硬上限，route 層再做業務驗證 |

**Post-Design Re-check**: 通過。新增端點 `GET /api/config` 僅讀取既有 `app.state.config`，不引入新狀態或依賴。

## Project Structure

### Documentation (this feature)

```text
specs/001-input-max-length/
├── plan.md              # 本文件
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── api-config.yaml  # Phase 1 output — OpenAPI fragment for GET /api/config
└── tasks.md             # Phase 2 output (/speckit.tasks command — NOT created here)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── config.py                  # 修改：加入 translation.max_input_length 預設值 512
│   ├── routes/
│   │   ├── config.py              # 新增：GET /api/config 端點
│   │   ├── translate.py           # 修改：translate_endpoint 加入長度驗證
│   │   └── __init__.py
│   └── schemas/
│       └── translation.py         # 修改：TranslationRequest.text max_length → 10000
└── tests/
    ├── unit/
    │   └── test_config_route.py   # 新增：GET /api/config 單元測試
    └── integration/
        └── test_translate_limit.py # 新增：長度驗證整合測試

frontend/
├── AppConfig.cs                   # 修改：新增 MaxInputLength 屬性，預設 512
├── Program.cs                     # 修改：啟動時呼叫 GET /api/config，更新 MaxInputLength
├── Components/
│   └── TranslationInput.razor     # 修改：接收 MaxInputLength 參數，取代硬碼 5000
└── Pages/
    └── Index.razor                # 修改：傳遞 AppCfg.MaxInputLength 給 TranslationInput

config.yaml                        # 修改：translation 區段新增 max_input_length: 512
config.example.yaml                # 修改：同上（保持同步）
```

**Structure Decision**: Option 2（Web application）。後端為 FastAPI Python 服務，前端為 Blazor WASM；本功能跨兩個子專案，但所有異動集中於既有檔案，無新目錄層級。
