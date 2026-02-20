# 快速入門指南

本指南協助您快速啟動 TranslateGemma 翻譯服務（後端 API + 前端 Web UI）。

---

## 環境需求

### 後端（FastAPI）
- **Python**: **3.13**（建議），3.11+ 可用但不支援 PyTorch CUDA wheel。請勿使用 Python 3.14（PyTorch CUDA wheel 尚未支援）
- **記憶體**: 4B 模型需 8GB+，12B 模型需 24GB+
- **GPU** (可選): NVIDIA CUDA 12.4+、Apple MPS（M 系列晶片）、或使用 CPU

### 前端（Blazor WASM）
- **.NET SDK**: 10.0+
- **瀏覽器**: Chrome/Edge/Firefox/Safari（支援 WASM）

### Docker 部署（可選）
- **Podman** 或 **Docker**: 最新版
- **Docker Compose/Podman Compose**

---

## 快速啟動（本地開發）

### 步驟 1：下載模型

從 Hugging Face 下載 TranslateGemma 模型至專案根目錄：

```bash
# 選擇其一
# 4B 模型（較快，記憶體需求較低）
huggingface-cli download google/TranslateGemma-4b-it \
  --local-dir models/Translategemma-4b-it

# 12B 模型（較精準，記憶體需求較高）
huggingface-cli download google/TranslateGemma-12b-it \
  --local-dir models/Translategemma-12b-it
```

**注意**：首次下載約需 10-30 分鐘（依網速與模型大小而定）。

---

### 步驟 2：建立設定檔

複製範例設定檔並調整參數：

```bash
cp config.example.yaml config.yaml
```

編輯 `config.yaml`：

```yaml
model:
  # 選擇模型：Translategemma-4b-it（快）或 Translategemma-12b-it（準）
  name: "Translategemma-4b-it"
  
  # 推論裝置：cuda（NVIDIA GPU）、mps（Apple M）、cpu（通用）
  device: "auto"  # 自動偵測最佳裝置
  
  # 模型目錄（相對專案根目錄）
  path: "models"

translation:
  # 最大輸入字元數
  max_length: 5000
  
  # 翻譯逾時（秒）
  timeout: 120
  
  # 預設語言對
  default_source: null  # null = 自動偵測
  default_target: null  # null = 智能切換

server:
  host: "0.0.0.0"
  port: 8000
  cors_origins:
    - "http://localhost:5000"  # Blazor WASM 開發埠
```

---

### 步驟 3：建立虛擬環境並安裝依賴

> **重要：請使用 Python 3.13**，PyTorch 的 CUDA wheel 尚不支援 Python 3.14。

**1. 確認已安裝 Python 3.13**

```powershell
# Windows - 列出所有已安裝的 Python 版本
py -0
# 應看到 -V:3.13 這一行；若無，請至 https://python.org 下載安裝 Python 3.13
```

**2. 建立虛擬環境**

```powershell
# Windows（明確使用 Python 3.13）
py -3.13 -m venv .venv
```

```bash
# Linux / macOS
python3.13 -m venv .venv
```

**3. 啟動虛擬環境**

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

> ⚠️ **新手注意**：啟動後，終端提示字元前方應出現 `(.venv)`。若未啟動就直接執行 `pip install`，會安裝到系統 Python 而非虛擬環境。

**4. 安裝依賴**

```powershell
# 使用 .venv 的 python（避免用到系統 pip）
python -m pip install -r backend/requirements.txt
```

> ⚠️ `pip install -r ...` 安裝的 `torch` 是 **CPU 版本**（版本號含 `+cpu`），GPU 推論需要額外步驟替換。

**5. 安裝 CUDA-enabled PyTorch（有 NVIDIA GPU 才需要）**

先確認 GPU 驅動版本：

```powershell
nvidia-smi
# 查看右上角 "CUDA Version" 欄位（顯示驅動最高支援版本）
# 例如：驅動支援 13.1，選擇 CUDA 12.4 的 PyTorch 即可（向下相容）
```

安裝（約 **2.5 GB**，請保持網路穩定並等待完成，中途不要中斷）：

```powershell
# 以 CUDA 12.4 為例（適用驅動版本 ≥ 550.x）
# 必須用 --force-reinstall 覆蓋掉上一步安裝的 CPU 版本
python -m pip install torch --force-reinstall --index-url https://download.pytorch.org/whl/cu124
```

> **版本號說明**：pytorch.org 的 CUDA wheel 版本號（如 `2.6.0+cu124`）會低於 PyPI 的 CPU 版號（如 `2.10.0`），版本號不同步是正常現象，不代表降版。

完整選項請至 https://pytorch.org/get-started/locally/ 選擇「Stable / Windows / Pip / Python / CUDA 12.x」。

**6. 驗證 CUDA 可用**

```powershell
python -c "import torch; print('torch:', torch.__version__); print('cuda:', torch.cuda.is_available()); print('device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no gpu')"
```

預期輸出：
```
torch: 2.6.0+cu124
cuda: True
device: NVIDIA GeForce RTX 4060
```

若 `cuda: False` 或版本含 `+cpu`，請參閱「常見問題排除 → 問題 6」。

**7. dtype 建議（依 VRAM 選擇）**

| VRAM | 建議 dtype | config.yaml 設定 |
|------|-----------|------------------|
| 8GB（如 RTX 4060） | `float16` | `dtype: "float16"` |
| 16GB+ | `bfloat16` | `dtype: "bfloat16"` |
| 24GB+（12B 模型） | `bfloat16` | `dtype: "bfloat16"` |

> **注意**：在 8GB GPU 上使用 `float32` 會導致 CUDA Out of Memory（OOM）錯誤，請避免。

**8. 啟動後端 API 伺服器**

```powershell
# 確保 .venv 已啟動（提示字元前有 (.venv)）
cd backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**首次啟動**：模型載入約需 30-60 秒，請等待終端顯示：
```
INFO:     Model loaded successfully on device: cuda
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### 步驟 4：啟動前端 UI

開啟新終端視窗：

```bash
cd frontend
dotnet restore
dotnet run
```

或使用 watch 模式（自動重新編譯）：

```bash
dotnet watch run
```

前端預設運行於 `http://localhost:5000`，開啟瀏覽器即可使用。

---

## Docker Compose 部署

### 一鍵啟動（推薦）

```bash
# 使用 Docker
docker-compose up -d

# 使用 Podman
podman-compose up -d
```

### 檢視服務狀態

```bash
docker-compose ps
# 或
podman-compose ps
```

### 檢視日誌

```bash
# 後端日誌
docker-compose logs -f backend

# 前端日誌
docker-compose logs -f frontend
```

### 停止服務

```bash
docker-compose down
# 或
podman-compose down
```

---

## 驗證安裝

### 1. 健康檢查

```bash
curl http://localhost:8000/health
```

預期回應：
```json
{
  "status": "ok",
  "model": "Translategemma-4b-it",
  "device": "cuda",
  "model_loaded": true,
  "uptime_seconds": 120
}
```

### 2. 翻譯測試（非串流）

```bash
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "source_lang": null,
    "target_lang": null,
    "stream": false
  }'
```

預期回應：
```json
{
  "translation": "你好，世界！",
  "source_lang": "en",
  "target_lang": "zh",
  "detected": true
}
```

### 3. 語言清單

```bash
curl http://localhost:8000/api/languages
```

預期回應：
```json
{
  "languages": [
    {"code": "en", "name": "English", "native_name": "English"},
    {"code": "zh-TW", "name": "Traditional Chinese", "native_name": "繁體中文"}
  ]
}
```

### 4. 前端 UI 測試

1. 開啟瀏覽器訪問 `http://localhost:5000`
2. 在輸入框輸入 "Hello, world!"
3. 點擊「翻譯」按鈕
4. 觀察右側顯示翻譯結果：「你好，世界！」

---

## 常見問題排除

### 問題 1：模型載入失敗

**症狀**：
```
ERROR: Model not found at models/Translategemma-4b-it
```

**解決方案**：
- 確認模型已下載至 `models/` 目錄
- 檢查 `config.yaml` 的 `model.path` 與 `model.name` 設定
- 執行 `ls models/` 確認目錄結構

---

### 問題 2：CUDA 記憶體不足

**症狀**：
```
RuntimeError: CUDA out of memory
```

**解決方案**：
1. 改用 4B 模型（記憶體需求較低）
2. 或在 `config.yaml` 設定 `device: "cpu"`
3. 或關閉其他耗用 GPU 的應用程式

---

### 問題 3：翻譯逾時

**症狀**：
```json
{
  "error": "timeout",
  "message": "翻譯逾時，請稍後重試"
}
```

**解決方案**：
- 調整 `config.yaml` 的 `translation.timeout`（預設 120 秒）
- 改用 4B 模型（推論速度較快）
- 或縮短輸入文字長度

---

### 問題 4：CORS 錯誤

**症狀**（瀏覽器主控台）：
```
Access to fetch at 'http://localhost:8000/api/translate' from origin 'http://localhost:5000' has been blocked by CORS policy
```

**解決方案**：
在 `config.yaml` 新增前端網址至 `server.cors_origins`：
```yaml
server:
  cors_origins:
    - "http://localhost:5000"
    - "http://localhost:5001"  # 如有多個埠
```

---

### 問題 5：前端白畫面

**症狀**：瀏覽器顯示空白頁面

**解決方案**：
1. 按 F12 開啟瀏覽器開發者工具
2. 檢查主控台（Console）錯誤訊息
3. 確認 .NET SDK 版本：`dotnet --version`（需 10.0+）
4. 清除快取並重新載入：`Ctrl + Shift + R`

---

### 問題 6：cuda: False（torch 安裝了 CPU 版本）

**症狀**：
```
cuda: False
torch: 2.x.x+cpu
```

**原因與解決方案**：

| 原因 | 解法 |
|------|------|
| 未啟動 `.venv` 就執行 `pip install` | 啟動 `.venv`（提示出現 `(.venv)`）再重新安裝 |
| 先裝了 `requirements.txt`（CPU torch），但未用 `--force-reinstall` 替換 | 重新執行：`python -m pip install torch --force-reinstall --index-url https://download.pytorch.org/whl/cu124` |
| `.venv` 使用 Python 3.14（無 CUDA wheel） | 確認：`python --version`；若是 3.14，請重建 .venv：`py -3.13 -m venv .venv` |
| 使用系統 `pip` 而非 `.venv` 的 `python -m pip` | 確保已用 `Activate.ps1` 啟動，或改用 `python -m pip install ...` |

---

## 效能基準

### 4B 模型（NVIDIA RTX 3090）
- **首次 token 延遲**: 5-10 秒
- **翻譯速度**: 約 10 token/秒
- **500 字元翻譯**: ~15 秒
- **記憶體使用**: ~8GB

### 12B 模型（NVIDIA RTX 4090）
- **首次 token 延遲**: 10-20 秒
- **翻譯速度**: 約 5 token/秒
- **500 字元翻譯**: ~30 秒
- **記憶體使用**: ~24GB

### CPU 模式（Apple M2 Max）
- **首次 token 延遲**: 20-40 秒
- **翻譯速度**: 約 2 token/秒
- **500 字元翻譯**: ~60 秒
- **記憶體使用**: ~12GB

**注意**：效能因硬體配置、輸入長度、語言對而異。

---

## 下一步

- **開發指南**: 參閱 `specs/001-gemma-translate-web/plan.md`
- **API 文件**: 參閱 `specs/001-gemma-translate-web/contracts/openapi.yaml`
- **資料模型**: 參閱 `specs/001-gemma-translate-web/data-model.md`
- **技術決策**: 參閱 `specs/001-gemma-translate-web/research.md`

---

## 授權

本專案採用 MIT 授權條款。
