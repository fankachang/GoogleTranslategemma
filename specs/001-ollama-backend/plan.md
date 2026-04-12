# 實作計畫：後端整合 Ollama 模型管理

**分支**：`001-ollama-backend` | **日期**：2026-04-12 | **規格**：[spec.md](spec.md)  
**輸入**：功能規格來自 `/specs/001-ollama-backend/spec.md`

## 摘要

在保留現有 local（行程內載入模型）後端架構完整不變的前提下，新增 `OllamaBackend` 實作，透過 `config.yaml` 的 `model.backend` 欄位讓使用者自由選擇推論後端。技術方向：新增 `backends/` 子套件（抽象介面 + LocalBackend + OllamaBackend），工廠函式 `create_backend()` 注入至 `main.py` lifespan；路由層不修改；術語注入、輸入限制在路由層處理，兩種後端均適用。

## 技術背景

**語言/版本**：Python 3.13（現有）  
**主要依賴**：FastAPI、Transformers（HuggingFace）、httpx（新增：Ollama HTTP 呼叫）  
**儲存**：N/A（無資料庫，設定檔為 YAML）  
**測試**：pytest + pytest-asyncio；mock 使用 `unittest.mock.AsyncMock`  
**目標平台**：Linux server / macOS（本機開發）  
**專案類型**：Web（frontend Blazor WASM + backend FastAPI）  
**效能目標**：翻譯回應 ≤ 30s（4B）；健康檢查逾時 ≤ 3s  
**限制**：不修改路由層 API 介面；不引入大型新依賴；`model.backend` 預設 `local` 確保向下相容  
**規模/範圍**：後端 Python 套件新增約 3 個檔案（`base.py`、`local.py`、`ollama.py`）；現有 `config.py`、`main.py`、`health.py` 小幅修改

## Constitution Check

*GATE: 規格設計前與設計後各驗證一次*

| 原則 | 檢查結果 | 說明 |
|------|---------|------|
| I. 在地化優先（不可妥協） | ✅ 通過 | 規格、計畫、文件均以繁體中文撰寫 |
| II. API 契約完整性 | ✅ 通過 | 路由層介面不異動；health 回應新增欄位向下相容；contracts/ 已定義 |
| III. 簡單原則 / YAGNI（不可妥協） | ✅ 通過 | 僅新增 3 個檔案 + 小幅修改 3 個現有檔案；不引入大型依賴；httpx 已在生態系中 |
| IV. 測試先行 | ✅ 通過 | 規劃新增 `test_ollama_backend.py`（單元）與整合測試擴充，測試需在實作前完成 |
| V. UI 版型一致性 | ✅ 通過（N/A） | 本功能無前端 UI 修改 |
| VI. 虛擬環境衛生 | ✅ 通過 | 使用現有 `.venv`，不建立新環境 |
| VII. 可觀察性與可除錯性 | ✅ 通過 | `OllamaBackend` 需實作結構化日誌：請求 URL、回應狀態碼、逾時事件；錯誤均需 logger.error |

**設計後重新評估（Phase 1 完成）**：

| 原則 | 重新確認 | 說明 |
|------|---------|------|
| III. YAGNI | ✅ 通過 | `backends/` 子套件僅為必要抽象；工廠函式為單一進入點，無過度設計 |
| II. API 契約 | ✅ 通過 | `health-api.yaml` 已定義擴充後的回應格式，現有欄位全數保留 |

## Project Structure

### 文件（本功能）

```text
specs/001-ollama-backend/
├── plan.md              # 本文件
├── research.md          # Phase 0 研究報告
├── data-model.md        # Phase 1 資料模型
├── quickstart.md        # Phase 1 快速上手指引
├── contracts/
│   └── health-api.yaml  # Phase 1 API 契約（health 端點擴充）
└── tasks.md             # Phase 2 輸出（由 /speckit.tasks 產生）
```

### 原始碼（異動範圍）

```text
backend/
├── src/
│   ├── backends/                        ← 新增子套件
│   │   ├── __init__.py                  ← 新增：匯出 create_backend() 工廠函式
│   │   ├── base.py                      ← 新增：TranslationBackend ABC
│   │   ├── local.py                     ← 新增：LocalBackend（現有 model.py 邏輯移入）
│   │   └── ollama.py                    ← 新增：OllamaBackend（httpx REST 呼叫）
│   ├── config.py                        ← 修改：新增 backend/ollama 設定預設值
│   ├── main.py                          ← 修改：lifespan 改用 create_backend()
│   ├── routes/
│   │   └── health.py                    ← 修改：回應新增 backend/ollama_url 欄位
│   └── model.py                         ← 不修改（LocalBackend 移入後可保留相容性引用）
├── tests/
│   ├── unit/
│   │   └── test_ollama_backend.py       ← 新增：OllamaBackend 單元測試（mock httpx）
│   └── integration/
│       └── test_api_endpoints.py        ← 修改：新增 ollama 後端場景
└── requirements.txt                     ← 修改：新增 httpx（若未列入）

config.example.yaml                      ← 修改：補充 backend/ollama 設定欄位說明
```

**結構決策**：採用 Web 架構（前後端分離），僅異動後端 Python 套件。前端（Blazor WASM）不需任何修改。
