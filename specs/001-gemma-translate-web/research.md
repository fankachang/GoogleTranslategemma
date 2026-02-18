# Research & Technical Decisions: TranslateGemma 網頁翻譯服務

**Feature**: 001-gemma-translate-web  
**Date**: 2026-02-17  
**Status**: ✅ Completed

## Overview

本文件記錄 TranslateGemma 網頁翻譯服務的技術決策、研究發現，以及替代方案評估。所有決策基於「簡單為主」的設計原則，避免過度設計。

---

## 1. 前端框架選擇

### Decision: Blazor WebAssembly (.NET 10)

**Rationale**:
- **WASM 優勢**: 完全運行在瀏覽器端，無需額外伺服器渲染，降低後端負擔
- **C# 生態**: 與 .NET 生態系統整合良好，類型安全、強大的工具鏈
- **MudBlazor**: 現成的 Material Design 元件庫，加速 UI 開發
- **響應式彈性**: 天然支援 SPA 架構，適合對話式介面

**Alternatives Considered**:

| 選項 | 優點 | 缺點 | 為何未採用 |
|------|------|------|------------|
| **React + TypeScript** | 生態系統龐大、社群活躍 | 需要額外學習曲線、工具鏈複雜 | 專案原始需求已指定 Blazor |
| **Vue.js** | 輕量、易學、中文文件豐富 | SPA 框架較年輕、企業採用率較低 | 團隊熟悉度不如 Blazor |
| **Vanilla JS + Lit** | 最小依賴、載入速度快 | 缺乏現成 UI 元件、開發效率低 | 對話式介面複雜度不適合純手寫 |

---

## 2. 後端框架選擇

### Decision: Python FastAPI

**Rationale**:
- **非同步優勢**: 原生支援 `async/await`，適合 SSE 串流與長時間模型推論
- **自動文件**: OpenAPI/Swagger 自動生成，便於前端對接
- **型別提示**: Pydantic 模型確保 API 合約類型安全
- **ML 生態**: Python 是 ML/AI 領域主流語言，與 Hugging Face Transformers 無縫整合

**Alternatives Considered**:

| 選項 | 優點 | 缺點 | 為何未採用 |
|------|------|------|------------|
| **Flask** | 輕量、簡單、社群成熟 | 缺乏原生非同步支援、SSE 需額外處理 | SSE 串流是核心需求，FastAPI 更適合 |
| **Node.js + Express** | JavaScript 全棧、非同步 I/O 原生 | Python ML 生態更成熟、模型載入較麻煩 | 模型推論在 Python 生態系更成熟 |
| **Go + Gin** | 高效能、編譯型語言 | 缺乏 ML 生態、模型推論需透過 gRPC 或 C binding | 增加系統複雜度，不符合簡單為主 |

---

## 3. 模型推論架構

### Decision: Hugging Face Transformers（直接載入）

**Rationale**:
- **官方支援**: TranslateGemma 由 Hugging Face 託管，直接使用官方 API
- **簡單部署**: 單機部署無需額外推論服務，降低運維複雜度
- **裝置彈性**: 支援 CUDA、MPS、CPU，透過 PyTorch 後端自動選擇
- **設定驅動**: 透過 `config.yaml` 切換 4B/12B 模型，無需改程式碼

**Alternatives Considered**:

| 選項 | 優點 | 缺點 | 為何未採用 |
|------|------|------|------------|
| **vLLM** | 高吞吐量、批次推論最佳化 | 複雜部署、記憶體需求高、overkill for single-user | 本專案無高並發需求 |
| **TensorRT-LLM** | NVIDIA 加速、極致效能 | 僅支援 NVIDIA、轉換模型複雜 | 需支援 MPS/CPU，TensorRT 太重 |
| **ONNX Runtime** | 跨平台、高效能 | 模型轉換額外步驟、debug 困難 | 增加部署複雜度，Transformers 已足夠 |
| **OpenAI API** | 免運維、高品質 | 需付費、無法控制模型版本、不符合本地部署需求 | 專案明確要求本地模型 |

---

## 4. 串流輸出機制

### Decision: Server-Sent Events (SSE)

**Rationale**:
- **單向串流**: 後端 → 前端單向推送，符合翻譯場景
- **原生支援**: FastAPI 透過 `StreamingResponse` 簡單實作，瀏覽器原生 `EventSource`
- **重連機制**: SSE 內建斷線重連，提升穩定性
- **文字友善**: 逐 token 推送為純文字，無需複雜序列化

**SSE 格式範例**:
```
data: {"token": "Hello", "done": false}\n\n
data: {"token": " world", "done": false}\n\n
data: {"token": "!", "done": true}\n\n
```

**Alternatives Considered**:

| 選項 | 優點 | 缺點 | 為何未採用 |
|------|------|------|------------|
| **WebSocket** | 雙向通訊、低延遲 | 過度設計（本場景無需前端→後端串流） | SSE 已足夠，WebSocket 增加複雜度 |
| **Long Polling** | 相容性極高 | 效率低、伺服器負擔重 | 現代瀏覽器均支援 SSE |
| **gRPC Streaming** | 高效能、類型安全 | 瀏覽器需 gRPC-Web proxy、複雜度高 | 本專案無微服務需求 |

---

## 5. 語言自動偵測

### Decision: 前端字元範圍檢測 + 後端確認

**Rationale**:
- **即時回饋**: 前端即時偵測，無需等待後端回應
- **簡單實作**: 初期僅支援繁體中文與英文，正則表達式即可處理：
  - 繁體中文: `/[\u4e00-\u9fa5]/` （Unicode CJK Unified Ideographs）
  - 英文: `/[a-zA-Z]/`
- **後端容錯**: 後端再次確認語言，避免前端誤判
- **擴展彈性**: 未來可替換為 `langdetect` 或 `fastText` 支援更多語言

**Detection Logic**:
```python
def detect_language(text: str) -> str:
    chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    
    if chinese_chars > english_chars:
        return "zh"
    elif english_chars > 0:
        return "en"
    else:
        return "unknown"  # Fallback to user manual selection
```

**Alternatives Considered**:

| 選項 | 優點 | 缺點 | 為何未採用 |
|------|------|------|------------|
| **langdetect** | 支援 55+ 語言、高準確度 | 額外依賴、短文本準確度降低 | 初期僅需繁體中文與英文，YAGNI |
| **fastText (語言識別模型)** | Meta 官方、準確度極高 | 模型檔案 130MB+、overkill | 本場景簡單正則即可 |
| **後端 API 呼叫 (如 Google Translate API)** | 準確度高、免運維 | 需網路、延遲高、不符合本地化需求 | 增加網路依賴，違反設計原則 |

---

## 6. 錯誤訊息顯示策略

### Decision: Toast (輕量) + 對話泡泡 (嚴重)

**Rationale**:
- **使用體驗分層**: 輕量錯誤不干擾對話流程，嚴重錯誤保留在歷史中便於追溯
- **Toast 自動消失**: 3-5 秒後消失，避免頁面堆積
- **對話泡泡保留**: 嚴重錯誤（如翻譯失敗、逾時）保留完整錯誤訊息
- **MudBlazor 支援**: MudBlazor 內建 `MudSnackbar`（Toast）元件，快速整合

**Error Classification**:

| 錯誤類型 | 顯示方式 | 範例 |
|---------|---------|------|
| **輕量錯誤** | Toast (3-5 秒) | 空白輸入、字數超過 5000、格式驗證失敗 |
| **嚴重錯誤** | 對話區域錯誤泡泡 | 翻譯失敗、後端無回應、模型未載入、逾時 |

**Alternatives Considered**:

| 選項 | 優點 | 缺點 | 為何未採用 |
|------|------|------|------------|
| **僅 Toast** | 介面簡潔、不干擾對話 | 嚴重錯誤消失後使用者無法查看 | 錯誤訊息追溯性差 |
| **僅對話泡泡** | 所有錯誤可追溯 | 輕量錯誤堆積影響可讀性 | 增加視覺噪音 |
| **Modal 對話框** | 強制使用者注意 | 干擾工作流程、需手動關閉 | 過度打斷使用者操作 |

---

## 7. 容器化策略

### Decision: Podman / Docker 相容

**Rationale**:
- **Containerfile**: 使用 Podman/Docker 通用的 Containerfile（而非 Dockerfile）
- **Compose 相容**: `docker-compose.yaml` 兩者通用
- **無 daemon 依賴**: Podman 無需常駐 daemon，更輕量
- **安全性**: Podman rootless mode 提供更好的安全隔離

**Deployment Structure**:
```yaml
# docker-compose.yaml
services:
  backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models:ro
      - ./config.yaml:/app/config.yaml:ro
    environment:
      - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
  
  # 前端編譯為靜態檔案，由 nginx 或任何 HTTP 伺服器提供
```

**Alternatives Considered**:

| 選項 | 優點 | 缺點 | 為何未採用 |
|------|------|------|------------|
| **Kubernetes** | 生產級編排、自動擴展 | 過度複雜、本專案無需編排 | 單機部署无需 K8s |
| **純 systemd 服務** | 無容器開銷 | 環境依賴管理困難、跨平台差 | 容器化提供更好的可移植性 |
| **Snap/Flatpak** | 應用隔離、自動更新 | 限於 Linux、缺乏多服務編排 | 專案需前後端協作，Compose 更適合 |

---

## 8. 測試策略

### Decision: Unit + Integration + E2E

**Test Coverage Plan**:

| 層級 | 工具 | 測試範圍 | 目標覆蓋率 |
|------|------|---------|-----------|
| **後端單元測試** | pytest | 模型載入、語言偵測、設定解析 | >80% |
| **後端整合測試** | pytest + TestClient | API endpoints、SSE streaming | >70% |
| **前端單元測試** | bUnit | 元件邏輯、服務層 | >70% |
| **E2E測試** | Playwright | 完整翻譯流程 | 關鍵路徑 |

**Rationale**:
- **金字塔結構**: 單元測試多、整合測試適中、E2E 測試少（成本考量）
- **快速回饋**: 單元測試秒級執行，CI/CD 友善
- **實際場景**: E2E 測試涵蓋使用者最常用的翻譯流程

---

## 9. 效能最佳化

### Decisions

#### 9.1 模型載入優化
- **Lazy Loading**: 啟動時僅載入設定，首次請求才載入模型（避免冷啟動過慢）
- **Model Caching**: 模型載入後常駐記憶體，避免重複載入
- **Device Auto**: `device="auto"` 讓 PyTorch 自動選擇最佳裝置

#### 9.2 前端優化
- **Blazor WASM Trimming**: 啟用 IL trimming 減少 WASM bundle 大小
- **Lazy Component Loading**: 對話記錄元件按需載入
- **Virtual Scrolling**: 翻譯記錄超過 50 筆時啟用虛擬滾動

#### 9.3 後端優化
- **無連接池**: 單機無需資料庫連接池
- **Async I/O**: 所有 I/O 操作使用 `async/await`
- **Timeout 控制**: 設定明確的 120 秒超時，避免請求堆積

---

## 10. 安全性考量

### Implemented Measures

| 威脅 | 緩解措施 | 實作方式 |
|------|---------|---------|
| **XSS 攻擊** | 輸入清洗 | Blazor 自動轉義 HTML、後端 Pydantic 驗證 |
| **SSRF** | 無外部請求 | 後端僅載入本地模型，無需對外連線 |
| **DoS** | 請求限制 | 5000 字元上限、120 秒超時 |
| **依賴漏洞** | 定期更新 | `pip-audit`, `dotnet list package --vulnerable` |
| **模型投毒** | 本地模型 | 不接受使用者上傳模型，僅使用官方 Hugging Face 模型 |

**HTTPS**: 生產環境建議使用 reverse proxy (如 nginx) 處理 TLS

---

## 11. 未來擴展考量

### Phase 2+ Potential Features

根據「簡單為主」原則，以下功能**不在初期範圍**，但可供未來擴展參考：

| 功能 | 優先順序 | 複雜度 | 備註 |
|------|--------|--------|------|
| **多語言自動偵測** | P2 | 中 | 整合 `langdetect` 或 `fastText` |
| **翻譯歷史匯出** | P3 | 低 | JSON / CSV 下載 |
| **深色模式** | P3 | 低 | MudBlazor 內建支援 |
| **reCAPTCHA** | P3 | 中 | 防止濫用（若公開部署） |
| **Redis 快取** | P4 | 中 | 快取常見翻譯（增加依賴） |
| **多模型比較** | P4 | 高 | 同時顯示 4B/12B 結果（記憶體需求高） |

這些功能需額外評估成本與收益，目前不影響 MVP 交付。

---

## Summary

所有技術決策均基於以下原則：
1. ✅ **簡單為主**: 避免過度設計，優先選擇成熟穩定的方案
2. ✅ **需求驅動**: 所有技術選型對應明確的功能需求
3. ✅ **可維護性**: 優先選擇文件齊全、社群活躍的技術
4. ✅ **效能可接受**: 在滿足效能目標前提下，避免過度優化

**Status**: ✅ All technical decisions documented and justified  
**Next Step**: Proceed to Phase 1 - Data Model & Contracts
