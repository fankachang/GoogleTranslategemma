# TranslateGemma 部署檢核清單

> 依序完成以下所有步驟，確保服務正確部署並可正常使用。

---

## 階段一：環境前置確認

- [ ] 確認目標主機作業系統（Linux x86_64 / macOS Apple Silicon）
- [ ] 確認 Python 版本 ≥ 3.10（`python3 --version`）
- [ ] 確認 .NET SDK 9 已安裝（`dotnet --version`，需顯示 `9.x.xxx`）
- [ ] 確認 Podman 或 Docker 已安裝並可執行（`podman info` / `docker info`）
- [ ] 確認磁碟可用空間：4B 模型約需 **10 GB**，12B 模型約需 **28 GB**
- [ ] 確認可用記憶體：4B 模型建議 ≥ **16 GB RAM / VRAM**，12B 建議 ≥ **32 GB**
- [ ] 確認網路可連線 Hugging Face（`curl -I https://huggingface.co` 回傳 200）

---

## 階段二：取得原始碼

```bash
git clone <REPO_URL> GoogleTranslateGemma
cd GoogleTranslateGemma
```

- [ ] 成功 clone 儲存庫
- [ ] 切換至正確分支（`git branch`）

---

## 階段三：模型下載

> 模型檔案不納入版本控制，需手動下載至 `models/` 目錄。

### 前置：取得 Gemma 授權

- [ ] 登入 [https://huggingface.co](https://huggingface.co) 並申請 Gemma 模型授權
- [ ] 產生 Hugging Face Access Token（Settings → Access Tokens）

### 下載 4B 模型

```bash
pip install huggingface-hub[cli]
huggingface-cli login          # 輸入 Access Token
huggingface-cli download google/translategemma-4b-it \
  --local-dir models/Translategemma-4b-it \
  --local-dir-use-symlinks False
```

- [ ] `models/Translategemma-4b-it/` 目錄存在且包含 `.safetensors` 與 `tokenizer.json`

### 下載 12B 模型（可選）

```bash
huggingface-cli download google/translategemma-12b-it \
  --local-dir models/Translategemma-12b-it \
  --local-dir-use-symlinks False
```

- [ ] `models/Translategemma-12b-it/` 目錄存在且包含 `.safetensors` 與 `tokenizer.json`

---

## 階段四：設定檔配置

```bash
cp config.example.yaml config.yaml
```

編輯 `config.yaml`，確認以下各項：

### 模型設定

- [ ] `model.name` 設為 `"4b"` 或 `"12b"`（與已下載的模型一致）
- [ ] `model.base_path` 設為 `"models"`（或模型實際存放的相對/絕對路徑）
- [ ] `model.device` 確認裝置選擇：
  - `"auto"` — 自動偵測 CUDA → MPS → CPU（推薦）
  - `"cuda"` — 強制使用 NVIDIA GPU
  - `"mps"` — 強制使用 Apple Silicon GPU
  - `"cpu"` — 僅使用 CPU（速度較慢）
- [ ] `model.dtype` 設為 `"auto"`（或依需求指定 `"bfloat16"` / `"float32"`）

### 伺服器設定

- [ ] `server.host` 設為 `"0.0.0.0"`（允許外部存取）或 `"127.0.0.1"`（僅本機）
- [ ] `server.port` 確認未與其他服務衝突（預設 `8000`）

### 翻譯設定

- [ ] `translation.timeout` 設為合適的逾時秒數（預設 `120`）
- [ ] `translation.max_new_tokens` 設為合適的生成上限（預設 `512`）

### 術語對照表（可選）

- [ ] 若需要術語替換，確認 `glossary.enabled: true` 並填入 `glossary.entries`
- [ ] 若不需要，確認 `glossary.enabled: false`

### 前端設定

編輯 `frontend/wwwroot/appsettings.json`：

- [ ] `BackendUrl` 設為後端 API 的可存取位址（例如 `"http://your-server:8000"`）
- [ ] `AppTitle` 設為顯示名稱（可保留預設 `"TranslateGemma"`）
- [ ] `AppLogoUrl` 設為 Logo 圖片路徑，或留空

---

## 階段五：本地開發驗證（非容器）

### 後端驗證

```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate     # Windows: ..\.venv\Scripts\activate
pip install -r requirements.txt
cd ..
python -m backend.src.main
```

- [ ] 後端服務啟動，終端顯示 `Uvicorn running on http://0.0.0.0:8000`
- [ ] `curl http://localhost:8000/health` 回傳 `{"status":"ok","model_loaded":true,...}`
- [ ] `model_loaded` 為 `true`（非 `false`）
- [ ] `resolved_device` 回傳預期裝置（`cuda` / `mps` / `cpu`）

### 後端單元 / 整合測試

```bash
cd backend
pytest tests/ -v
```

- [ ] 所有測試通過（`passed`，無 `failed` 或 `error`）

### 前端驗證

```bash
cd frontend
dotnet run --project frontend.csproj
```

- [ ] 前端服務啟動，顯示監聽於 `http://localhost:5000`
- [ ] 瀏覽器開啟 `http://localhost:5000` 顯示 TranslateGemma 介面

---

## 階段六：容器部署

### 使用 Podman Compose

```bash
podman-compose up --build -d
```

### 使用 Docker Compose

```bash
docker-compose up --build -d
```

- [ ] 兩個容器均啟動成功（`backend`、`frontend`）
- [ ] `podman ps` / `docker ps` 顯示兩個容器狀態為 `Up`（非 `Exiting`）

---

## 階段七：部署後健康驗證

### 後端健康檢查

```bash
curl http://localhost:8000/health
```

預期回應：

```json
{
  "status": "ok",
  "model_name": "4b",
  "device": "auto",
  "resolved_device": "mps",
  "model_loaded": true
}
```

- [ ] `status` 為 `"ok"`
- [ ] `model_loaded` 為 `true`
- [ ] `resolved_device` 為預期裝置

### 翻譯功能驗證

```bash
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!", "stream": false}'
```

- [ ] 回應 HTTP 200
- [ ] `translated_text` 包含繁體中文譯文（如「你好，世界！」）
- [ ] `source_lang` 為 `"en"`
- [ ] `target_lang` 為 `"zh-TW"`

### 語言清單驗證

```bash
curl http://localhost:8000/api/languages
```

- [ ] 回傳陣列包含 `zh-TW` 與 `en` 兩筆記錄

### 術語對照表端點驗證

```bash
curl http://localhost:8000/api/glossary
```

- [ ] 回傳 `{"enabled": true/false, "entries": [...]}`（無 HTTP 錯誤）

### 前端介面驗證

- [ ] 瀏覽器開啟前端網址，介面正常顯示（深色模式預設）
- [ ] 輸入「Hello, how are you?」並點擊「翻譯」
- [ ] 約 10–30 秒後顯示繁體中文譯文
- [ ] 點擊右上角 `...` 圖示，術語對照表面板正常開啟
- [ ] 點擊主題切換按鈕，可在亮色 / 暗色模式間切換
- [ ] 重新整理頁面後，主題偏好設定保持不變（`localStorage` 記憶）

---

## 階段八：CORS 與網路設定確認

> 若前端與後端部署在不同網域 / Port，需確認以下設定。

- [ ] `config.yaml` 中 `cors.allow_origins` 包含前端實際網址（避免使用 `"*"` 於正式環境）
- [ ] 防火牆已開放後端 Port（預設 `8000`）與前端 Port（預設 `5000`）
- [ ] 若使用反向代理（Nginx / Caddy），確認代理設定正確轉發請求

---

## 階段九：正式環境安全性確認

- [ ] `config.yaml` 不納入版本控制（已在 `.gitignore` 中排除）
- [ ] `cors.allow_origins` 限縮為實際的前端網域（非 `"*"`）
- [ ] 後端 Port（8000）不直接對外暴露，建議透過反向代理
- [ ] 模型檔案目錄 (`models/`) 不對外提供靜態存取

---

## 快速驗證指令彙整

```bash
# 後端健康
curl http://localhost:8000/health

# 翻譯測試（非串流）
curl -sX POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello","stream":false}' | python3 -m json.tool

# 語言清單
curl -s http://localhost:8000/api/languages | python3 -m json.tool

# 術語對照表
curl -s http://localhost:8000/api/glossary | python3 -m json.tool

# 前端首頁可存取
curl -sI http://localhost:5000 | head -1
```
