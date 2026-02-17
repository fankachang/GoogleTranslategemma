# 001 — TranslateGemma 翻譯網頁服務需求規格

## 1. 專案概述

建立一個類似 ChatGPT 對話介面的網頁翻譯服務，後端串接本地 TranslateGemma 模型（4B / 12B），讓使用者透過瀏覽器即可進行多語言文字翻譯。

> **設計原則**：簡單為主，不需帳號管理、不需持久化歷史紀錄（關閉頁面即清除），僅支援文字翻譯。

## 2. 系統架構

```
┌──────────────┐          HTTP/SSE          ┌──────────────────┐
│   前端 SPA    │  ◄──────────────────────► │   後端 API 服務   │
│ (Blazor WASM) │                            │   (FastAPI)      │
└──────────────┘                            └────────┬─────────┘
                                                        │
                                                        ▼
                                               ┌──────────────────┐
                                               │  TranslateGemma  │
                                               │  4B / 12B 模型   │
                                               └──────────────────┘
```

- **前端**：Blazor WebAssembly (WASM) 單頁應用，完全在瀏覽器端運行，提供類似 ChatGPT 的對話式翻譯介面
- **後端**：Python FastAPI，負責接收翻譯請求、呼叫模型、回傳結果
- **模型**：本地載入 TranslateGemma-4b-it 或 TranslateGemma-12b-it（透過設定檔切換）

## 3. 功能需求

### 3.1 前端功能

| 編號 | 功能 | 說明 |
|------|------|------|
| F-01 | 對話式翻譯介面 | 類似 ChatGPT 的聊天泡泡布局；左側顯示使用者輸入原文，右側顯示翻譯結果 |
| F-02 | 來源/目標語言選擇 | 提供下拉選單讓使用者選擇來源語言與目標語言（支援模型涵蓋的 55 種語言） |
| F-03 | 文字翻譯 | 使用者於輸入框輸入文字，送出後顯示翻譯結果 |
| F-04 | 串流輸出（Streaming） | 翻譯結果以串流方式逐步呈現，提升使用者體驗 |
| F-05 | 複製結果 | 翻譯結果旁提供一鍵複製按鈕 |
| F-06 | 響應式佈局 | 支援桌面與行動裝置瀏覽 |
| F-07 | 記憶體內歷史 | 當次瀏覽期間的翻譯紀錄保留於頁面中，關閉或重新整理即清除，不做持久化儲存 |

### 3.2 後端功能

| 編號 | 功能 | 說明 |
|------|------|------|
| B-01 | 翻譯 API | 接收原文、來源語言碼、目標語言碼，回傳翻譯結果 |
| B-02 | 串流回應 | 支援 SSE (Server-Sent Events) 串流回傳翻譯結果 |
| B-03 | 模型設定檔切換 | 透過設定檔（如 `config.yaml`）指定使用 4B 或 12B 模型，無需改程式碼 |
| B-04 | 語言清單 API | 回傳模型支援的語言清單，供前端下拉選單使用 |
| B-05 | 健康檢查 API | 提供 `/health` 端點確認服務與模型狀態 |
| B-06 | GPU 裝置支援 | 支援 Apple MPS、NVIDIA CUDA、CPU 三種推論裝置，透過設定檔 `device` 欄位切換 |

### 3.3 設定檔

設定檔路徑：專案根目錄 `config.yaml`

```yaml
# 模型設定
model:
  # 可選值: "4b" | "12b"
  name: "4b"
  # 模型存放路徑（相對於專案根目錄）
  base_path: "models"
  # 推論裝置: "auto" | "cpu" | "cuda" | "mps"
  # auto 會依序偵測: cuda → mps → cpu
  device: "auto"
  # 資料型別: "auto" | "bfloat16" | "float16" | "float32"
  # auto 會依裝置自動選擇: CUDA/MPS → bfloat16, CPU → float32
  dtype: "auto"

# 伺服器設定
server:
  host: "0.0.0.0"
  port: 8000

# 翻譯設定
translation:
  max_new_tokens: 512
  timeout: 120
```

模型路徑對應規則：
- `name: "4b"` → `{base_path}/Translategemma-4b-it`
- `name: "12b"` → `{base_path}/Translategemma-12b-it`

## 4. 非功能需求

| 編號 | 項目 | 說明 |
|------|------|------|
| NF-01 | 效能 | 單次文字翻譯回應時間（不含模型載入）≤ 30 秒 (4B) / ≤ 60 秒 (12B) |
| NF-02 | 相容性 | 支援 Chrome、Firefox、Safari、Edge 最新版本 |
| NF-03 | 安全性 | 前後端通訊使用 HTTPS（生產環境）；輸入內容需做基本清洗防 XSS |
| NF-04 | 可維護性 | 前後端程式碼結構清晰，遵循各自框架慣例 |
| NF-05 | 部署方式 | 支援 Podman / Docker，提供 Compose 檔案一鍵啟動（前端 + 後端） |

## 5. 技術選型

| 層級 | 技術 |
|------|------|
| 前端框架 | Blazor WebAssembly (.NET 10) |
| 前端 UI | MudBlazor 元件庫 |
| 後端框架 | Python FastAPI |
| 模型推論 | Hugging Face Transformers (`AutoModelForImageTextToText`, `AutoProcessor`) |
| GPU 支援 | NVIDIA CUDA（Linux/Windows）、Apple MPS（macOS）、CPU fallback |
| 設定管理 | PyYAML 讀取 `config.yaml` |
| 容器化 | Podman / Docker + Compose（相容兩者） |

## 6. API 規格概要

### 6.1 `POST /api/translate`

文字翻譯（支援 SSE 串流）。

**Request Body:**
```json
{
  "text": "要翻譯的文字",
  "source_lang": "en",
  "target_lang": "zh-TW",
  "stream": true
}
```

**Response（非串流）：**
```json
{
  "translation": "翻譯結果",
  "source_lang": "en",
  "target_lang": "zh-TW"
}
```

**Response（串流）：** SSE 格式，逐 token 回傳。

### 6.2 `GET /api/languages`

取得支援的語言清單。

**Response:**
```json
{
  "languages": [
    { "code": "en", "name": "English" },
    { "code": "zh-TW", "name": "Chinese" },
    ...
  ]
}
```

### 6.3 `GET /health`

健康檢查。

**Response:**
```json
{
  "status": "ok",
  "model": "Translategemma-4b-it",
  "device": "cuda"
}
```

## 7. 專案目錄結構（規劃）

```
GoogleTranslateGemma/
├── .gitignore               # Git 忽略清單（models/、敏感資料等）
├── README.md                # 專案說明與模型下載指引
├── config.example.yaml      # 設定檔範例
├── config.yaml              # 模型與伺服器設定檔（使用者建立，已忽略）
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 設定檔載入
│   ├── model.py             # 模型載入與推論邏輯
│   ├── routes/
│   │   ├── translate.py     # 文字翻譯 API 路由
│   │   ├── languages.py     # 語言清單 API 路由
│   │   └── health.py        # 健康檢查路由
│   └── requirements.txt     # Python 依賴
├── frontend/
│   ├── Pages/                # Blazor 頁面元件 (.razor)
│   ├── Components/           # 共用元件
│   ├── Services/             # API 呼叫封裝 (HttpClient)
│   ├── wwwroot/              # 靜態資源
│   ├── Program.cs            # Blazor WASM 入口
│   └── frontend.csproj       # .NET 專案檔
├── models/                  # 模型檔案（已存在）
│   ├── Translategemma-4b-it/
│   └── Translategemma-12b-it/
├── Docs/
│   └── 001_requestment.md   # 本文件
├── docker-compose.yaml      # 相容 Podman Compose / Docker Compose
├── Containerfile             # 後端容器映像（Podman/Docker 通用）
└── AGENTS.md
```

## 8. 支援語言（模型涵蓋 55 語言，擷取常用清單）

模型支援語言碼採用 ISO 639-1 格式，亦可加上地區碼（如 `zh-TW`、`en-US`）。完整語言列表由模型 chat template 中定義，以下列出常用語言：

| 語言碼 | 語言 | 語言碼 | 語言 |
|--------|------|--------|------|
| en | English | zh / zh-TW | Chinese |
| ja | Japanese | ko | Korean |
| fr | French | de | German |
| es | Spanish | pt | Portuguese |
| ru | Russian | it | Italian |
| ar | Arabic | hi | Hindi |
| th | Thai | vi | Vietnamese |
| id | Indonesian | tr | Turkish |
| pl | Polish | nl | Dutch |
| cs | Czech | sv | Swedish |

## 9. 里程碑

| 階段 | 內容 |
|------|------|
| M1 | 後端 API 基礎架構 + 模型載入 + 文字翻譯 API（支援 MPS / CUDA / CPU） |
| M2 | 前端對話介面 + 串接文字翻譯 API |
| M3 | 串流輸出 (SSE) |
| M4 | Podman / Docker Compose 部署 |
