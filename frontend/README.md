# Frontend — TranslateGemma UI

基於 **Blazor WebAssembly** (.NET 9) + **MudBlazor** 的翻譯前端介面。

## 技術棧

| 元件 | 版本 |
|------|------|
| .NET | 9.0 |
| Blazor WebAssembly | 9.x |
| MudBlazor | 7.x |

## 目錄結構

```
frontend/
├── frontend.csproj
├── Program.cs                      # WASM 進入點，服務註冊
├── _Imports.razor                  # 全域 using 宣告
├── Containerfile.frontend          # 容器構建（nginx）
├── Models/
│   ├── Language.cs                 # 語言資料模型
│   ├── TranslationHistory.cs       # 翻譯歷史紀錄
│   ├── TranslationRequest.cs       # 翻譯請求模型
│   └── TranslationResponse.cs      # 翻譯回應模型
├── Services/
│   ├── ITranslationService.cs      # 翻譯服務介面 + StreamToken
│   ├── TranslationService.cs       # HTTP + SSE 串流實作
│   └── LanguageService.cs          # 語言清單快取服務
├── Components/
│   ├── TranslationInput.razor      # 輸入框（MudTextField + 字數計數）
│   ├── LanguageSelector.razor      # 語言下拉選單
│   ├── ChatBubble.razor            # 對話泡泡（原文右藍、譯文左灰、錯誤紅）
│   └── ToastNotification.razor     # Toast 通知（自動消失 5 秒）
├── Pages/
│   └── Index.razor                 # 主頁面（整合所有元件）
└── wwwroot/
    ├── index.html                  # HTML shell
    └── js/
        └── clipboard.js            # JSInterop helpers（複製、捲動）
```

## 快速開始

### 環境需求

- [.NET 9 SDK](https://dotnet.microsoft.com/download/dotnet/9.0)

### 安裝依賴

```bash
cd frontend
dotnet restore
```

### 開發模式啟動

```bash
cd frontend
dotnet run
```

前端預設在 `http://localhost:5000` 運行，後端 API 預設指向 `http://localhost:8000`。

### 自訂後端 API 位址

在 `frontend/wwwroot/appsettings.json`（或 `appsettings.Development.json`）中設定：

```json
{
  "BackendUrl": "http://localhost:8000"
}
```

## 主要功能

- **語言選擇**：來源語言支援「自動偵測」，目標語言固定選擇
- **語言交換**：點擊交換按鈕快速切換語言對
- **串流翻譯**：逐 token 顯示翻譯結果，不需等待完整回應
- **對話歷史**：保留本次工作階段的所有翻譯記錄（最多 50 筆）
- **複製按鈕**：點擊複製譯文，顯示「已複製」2 秒回饋
- **取消翻譯**：翻譯進行中可點擊「取消」中斷串流
- **Toast 通知**：輕量提示錯誤或警告訊息

## 容器化

使用 `Containerfile.frontend` 構建：

```bash
podman build -t translategemma-frontend -f Containerfile.frontend .
```

構建流程：
1. 使用 `dotnet/sdk:9.0` 發行 Blazor WASM 靜態檔案
2. 使用 `nginx:alpine` 提供靜態檔案服務（含 SPA fallback）
