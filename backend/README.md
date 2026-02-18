# Backend — TranslateGemma API

基於 **FastAPI** 的翻譯後端服務，呼叫本地 TranslateGemma 模型提供翻譯 API。

## 技術棧

| 元件 | 版本 |
|------|------|
| Python | 3.11+ |
| FastAPI | latest |
| Uvicorn | latest |
| Transformers | 4.x+ |
| PyYAML | latest |

## 目錄結構

```
backend/
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── config.py           # 載入 config.yaml
│   ├── language_detect.py  # 語言自動偵測
│   ├── main.py             # FastAPI app 進入點
│   ├── model.py            # TranslateGemmaModel 封裝
│   ├── routes/
│   │   ├── health.py       # GET /health
│   │   ├── languages.py    # GET /api/languages
│   │   └── translate.py    # POST /api/translate
│   └── schemas/
│       ├── language.py     # Language Pydantic 模型
│       └── translation.py  # TranslationRequest/Response Pydantic 模型
└── tests/
    ├── conftest.py
    ├── integration/
    │   └── test_api_endpoints.py
    └── unit/
        ├── test_config.py
        ├── test_glossary.py
        ├── test_language_detect.py
        └── test_model.py
```

## 快速開始

### 建立虛擬環境

```bash
cd /path/to/project
python3 -m venv .venv
source .venv/bin/activate
```

### 安裝依賴

```bash
pip install -r backend/requirements.txt
```

### 設定

```bash
cp config.example.yaml config.yaml
# 依需求編輯 config.yaml
```

### 啟動開發伺服器

```bash
uvicorn backend.src.main:app --reload --port 8000
```

## API 端點

| 方法 | 路徑 | 描述 |
|------|------|------|
| GET | `/health` | 服務健康狀態 |
| GET | `/api/languages` | 支援語言清單 |
| POST | `/api/translate` | 翻譯（支援 JSON 與 SSE 串流） |

### POST /api/translate

**請求：**
```json
{
  "text": "Hello world",
  "source_lang": "en",
  "target_lang": "zh-TW",
  "stream": false
}
```

- `source_lang`：來源語言（`en` / `zh-TW`，留空則自動偵測）
- `target_lang`：目標語言（`en` / `zh-TW`）
- `stream`：`true` 時以 SSE 串流回傳逐 token 結果

**SSE 串流格式：**
```
data: {"token": "你", "done": false}
data: {"token": "好", "done": false}
data: {"token": "", "done": true, "source_lang": "en", "target_lang": "zh-TW", "detected": true, "model_name": "4b"}
```

## 執行測試

```bash
# 在專案根目錄
source .venv/bin/activate
pytest backend/tests/ -v
```

## 設定檔說明

`config.yaml` 主要設定項目：

```yaml
model:
  name: "4b"         # "4b" 或 "12b"
  device: "auto"     # auto / cuda / mps / cpu
  dtype: "auto"      # auto / bfloat16 / float32
  max_new_tokens: 512
  base_path: "models"

server:
  host: "0.0.0.0"
  port: 8000
  timeout: 120       # 翻譯逾時秒數

cors:
  origins:
    - "http://localhost:5000"

glossary:
  enabled: false
  entries:
    - source: "AI"
      target: "人工智慧"
      lang_pair: "en-zh-TW"
```
