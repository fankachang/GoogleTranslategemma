# TranslateGemma 翻譯網頁服務

基於 Google TranslateGemma 模型的本地翻譯網頁服務，提供類似 ChatGPT 的對話式翻譯介面。

## 📋 專案特色

- 🌐 **前端**：Blazor WebAssembly (.NET 9) + MudBlazor，完全在瀏覽器運行
- ⚡ **後端**：FastAPI (Python)，高效能非同步 API，支援 SSE 串流
- 🤖 **模型**：TranslateGemma 4B / 12B，支援繁體中文 ↔ 英文雙向翻譯
- 🎯 **簡單設計**：無帳號管理、無持久化，關閉即清除
- 🖥️ **多裝置支援**：NVIDIA CUDA、Apple MPS、CPU

## 🚀 快速開始

### 前置需求

- Python **3.13**（建議，支援 PyTorch CUDA wheel）；3.10+ 可用但不支援 GPU 推論，請勿使用 3.14
- .NET 9 SDK
- Podman 或 Docker（容器部署）
- （選用）NVIDIA GPU with CUDA 或 Apple Silicon Mac（加速推論）

### 1. 下載模型

由於模型檔案過大，需手動下載至專案 `models/` 目錄：

#### 方法一：使用 Hugging Face CLI（推薦）

```bash
# 安裝 Hugging Face CLI
pip install huggingface-hub[cli]

# 登入 Hugging Face（需先申請 Gemma 授權）
huggingface-cli login

# 下載 4B 模型
huggingface-cli download google/translategemma-4b-it \
  --local-dir models/Translategemma-4b-it \
  --local-dir-use-symlinks False

# 下載 12B 模型
huggingface-cli download google/translategemma-12b-it \
  --local-dir models/Translategemma-12b-it \
  --local-dir-use-symlinks False
```

#### 方法二：使用 Git LFS

```bash
# 安裝 Git LFS
git lfs install

# 克隆模型倉庫
cd models
git clone https://huggingface.co/google/translategemma-4b-it Translategemma-4b-it
git clone https://huggingface.co/google/translategemma-12b-it Translategemma-12b-it
```

### 2. 設定檔

複製範例設定檔並根據需求調整：

```bash
cp config.example.yaml config.yaml
```

編輯 `config.yaml`：

```yaml
model:
  name: "4b"           # 選擇 "4b" 或 "12b"
  device: "auto"       # 自動偵測 cuda → mps → cpu
  dtype: "auto"        # 自動選擇精度
```

> **GPU 使用注意**：`pip install torch` 預設可能只安裝 CPU 版本（可用 `python -c "import torch; print(torch.__version__)"` 確認，若輸出含 `+cpu` 表示 CPU 版）。
> 需另行安裝 CUDA-enabled 版本：
> ```bash
> # CUDA 12.4（適用驅動版本 ≥ 550.x，如 RTX 4060）
> pip install torch --index-url https://download.pytorch.org/whl/cu124
> ```
> 完整安裝指令請至 https://pytorch.org/get-started/locally/ 選擇。
>
> **dtype 建議**：8GB GPU（如 RTX 4060）請使用 `dtype: "float16"`；`float32` 會導致 OOM。

### 3. （選用）啟用 GPU 容器加速

容器內使用 NVIDIA GPU 推論需在**主機**安裝 NVIDIA Container Toolkit，讓 Podman / Docker 能將 GPU 裝置傳遞給容器；`config.yaml` 同時需設定 `device: "cuda"`。

> 若無 GPU 或不需要 GPU 加速，可跳過此節，直接執行 `podman-compose up` 即可以 CPU / MPS 模式執行。GPU 設定已獨立至 `docker-compose.gpu.yaml`，僅 Windows NVIDIA 環境才需帶入。

#### Linux 主機

```bash
# 1. 安裝 NVIDIA Container Toolkit（Ubuntu / Debian）
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit

# 2. 產生 CDI 設定（Podman 必要）
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml

# 3.（若使用 Docker）設定 Docker runtime 並重啟
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 4. 驗證 GPU 可被容器存取
# Podman：
podman run --rm --device nvidia.com/gpu=all docker.io/nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
# Docker：
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

#### Windows（Podman Desktop + WSL2）

Podman Desktop for Windows 透過 `podman machine`（WSL2 虛擬機）執行容器，需進入機器內安裝：

```powershell
# 1. Windows 主機安裝 NVIDIA 驅動 ≥ 470.x（已含 WSL2 GPU 支援）
#    下載：https://www.nvidia.com/Download/index.aspx

# 2. 進入 podman machine
podman machine ssh

# ── 以下在 podman machine 內執行 ──────────────────────────────────
# 3. 安裝 nvidia-container-toolkit（預設 Fedora CoreOS 使用 rpm-ostree）
sudo rpm-ostree install nvidia-container-toolkit
sudo systemctl reboot   # 套用後重開機

# 4. 重新進入，產生 CDI 設定
# （在 Windows 端）
podman machine ssh
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml

# 5. 驗證
podman run --rm --device nvidia.com/gpu=all docker.io/nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
exit
```

> **版本需求**：Podman Desktop ≥ 1.3、Podman Engine ≥ 4.7 才支援 GPU 直通。

#### 設定 config.yaml 啟用 CUDA

```yaml
model:
  device: "cuda"   # 明確指定使用 NVIDIA GPU
  dtype: "float16" # 8 GB VRAM（如 RTX 4060）建議使用 float16
```

### 4. 啟動服務

依環境選擇對應部署方式：

| 環境 | 後端 | 前端 | MPS/GPU |
|------|------|------|---------|
| Linux / Windows 正式 | 容器 | 容器 | CUDA（需另帶 GPU override） |
| macOS Apple Silicon 正式 | **本機執行** | 容器 | ✅ MPS |
| 本地開發 | 本機（--reload） | dotnet run | ✅ MPS |

---

#### 容器部署（Linux / Windows 正式環境）

> Podman / Docker 在 macOS 透過 Linux VM 執行容器，**Metal / MPS 無法穿透**，macOS 請改用下方「macOS 正式部署」。

```bash
# 一般環境（CPU）
podman-compose up -d

# Windows + NVIDIA GPU（帶入 GPU override）
podman-compose -f docker-compose.yaml -f docker-compose.gpu.yaml up -d
```

Docker Compose 同理：

```bash
docker-compose up -d
docker-compose -f docker-compose.yaml -f docker-compose.gpu.yaml up -d
```

> **GPU 直通說明**：GPU 設定已獨立至 `docker-compose.gpu.yaml`，預設不帶入，避免非 NVIDIA 環境因找不到 CDI 裝置而報錯。

---

#### macOS Apple Silicon 正式部署（MPS 加速）

後端需本機執行才能存取 Metal/MPS；前端靜態檔案仍可透過容器以 nginx 服務。

**步驟一：啟動前端容器**

```bash
cd frontend
podman build -t translategemma-frontend .
podman run -d --name translategemma-frontend -p 5000:80 translategemma-frontend
```

**步驟二：本機啟動後端（正式模式，無 hot-reload）**

```bash
source .venv/bin/activate
uvicorn src.main:app --app-dir backend --host 0.0.0.0 --port 8000 --workers 1
```

> `config.yaml` 設定 `device: "auto"` 即可自動偵測 MPS；若需明確指定請設為 `device: "mps"`。

---

#### 本地開發

> 以下啟用 hot-reload，**僅供開發使用**，不建議用於正式服務。

**後端（支援程式碼異動自動重啟）：**

```bash
source .venv/bin/activate
uvicorn src.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```

**前端（dotnet watch，支援 Hot Reload）：**

```bash
dotnet run --project frontend/frontend.csproj
```

Windows PowerShell 亦可一行啟動後端：

```powershell
.venv\Scripts\Activate.ps1; uvicorn src.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```

### 5. 前端外觀設定

前端可透過 `frontend/wwwroot/appsettings.json` 自訂顯示設定：

```json
{
  "BackendUrl": "http://localhost:8000",
  "AppTitle": "TranslateGemma",
  "AppLogoUrl": "",
  "ContentWidthPercent": 80
}
```

| 欄位 | 說明 | 預設値 |
|------|------|------|
| `BackendUrl` | 後端 API 位址 | `http://localhost:8000` |
| `AppTitle` | 頁面標題及左上角顯示名稱 | `TranslateGemma` |
| `AppLogoUrl` | 左上角 Logo 圖片路徑（相對於 `wwwroot`，例如 `/images/logo.png`）；**空白則不顯示圖示** | `""` |
| `ContentWidthPercent` | 對話氣泡與輸入框的內容區塊寬度（佔瀏覽器視窗百分比，有效範圍 40–90 100） | `80` |

**Logo 使用範例：**

1. 將圖片放至 `frontend/wwwroot/images/logo.png`
2. 在 `appsettings.json` 中設定：

```json
{
  "AppTitle": "我的翻譯服務",
  "AppLogoUrl": "/images/logo.png"
}
```

> **佈景主題**：預設使用暗色模式，可在頁面右上角點擊圖示切換亮色 / 暗色，偏好設定會儲存在瀏覽器 `localStorage`。

### 6. 訪問服務

- **前端介面**：http://localhost:5000
- **後端 API 文件**：http://localhost:8000/docs

## 📖 文件

- [需求規格書](Docs/001_requestment.md)
- [API 文件](http://localhost:8000/docs)（服務啟動後可存取）

## 🛠️ 技術棧

| 層級 | 技術 |
|------|------|
| 前端 | Blazor WebAssembly (.NET 9) + MudBlazor |
| 後端 | Python FastAPI |
| 模型 | Google TranslateGemma (Hugging Face Transformers) |
| 推論加速 | CUDA / MPS / CPU |
| 容器化 | Podman / Docker |

## 🌍 支援語言

本服務目前支援 **繁體中文 (zh-TW) ↔ 英文 (en)** 雙向翻譯。

來源語言可選擇「自動偵測」，系統會根據輸入文字自動判斷語言。

## 📝 授權

本專案基於 [Gemma License](https://ai.google.dev/gemma/terms) 使用 Google TranslateGemma 模型。使用前請確保已閱讀並同意 Google 的使用條款。

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## ⚠️ 注意事項

- 模型檔案已加入 `.gitignore`，請勿將其提交至版本控制系統
- 敏感資料（`.env`、`*.key` 等）已自動忽略
- 首次啟動會載入模型，根據硬體配置可能需要數分鐘
- 4B 模型約需 8GB VRAM，12B 模型約需 24GB VRAM
- CPU 模式可運行但速度較慢
- **容器部署記憶體需求**：safetensors mmap 使用一般虛擬記憶體，需確保 VM / 容器有足夠總記憶體（4B ≈ 8GB、12B ≈ 24GB）。
- macOS 調整方式：`podman machine set --memory 20480`；Windows 於 Podman 同指令或 `.wslconfig` 調整；Docker Desktop 在 Resources → Memory 設定
