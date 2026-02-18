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

- Python 3.10+
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

### 3. 啟動服務

#### 使用 Podman Compose（推薦）

```bash
podman-compose up
```

#### 使用 Docker Compose

```bash
docker-compose up
```

#### 本地開發

**後端：**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**前端：**
```bash
cd frontend
dotnet restore
dotnet run
```

### 4. 前端外觀設定

前端可透過 `frontend/wwwroot/appsettings.json` 自訂顯示設定：

```json
{
  "BackendUrl": "http://localhost:8000",
  "AppTitle": "TranslateGemma",
  "AppLogoUrl": ""
}
```

| 欄位 | 說明 | 預設值 |
|------|------|--------|
| `BackendUrl` | 後端 API 位址 | `http://localhost:8000` |
| `AppTitle` | 頁面標題及左上角顯示名稱 | `TranslateGemma` |
| `AppLogoUrl` | 左上角 Logo 圖片路徑（相對於 `wwwroot`，例如 `/images/logo.png`）；**空白則不顯示圖示** | `""` |

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

### 5. 訪問服務

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
