# Data Model: TranslateGemma 網頁翻譯服務

**Feature**: 001-gemma-translate-web  
**Date**: 2026-02-17  
**Status**: ✅ Defined

## Overview

本文件定義 TranslateGemma 網頁翻譯服務的資料模型，包含實體、屬性、關係和狀態轉換。由於服務採用無狀態設計，所有資料模型僅用於請求/回應傳遞和前端記憶體儲存，**無需資料庫持久化**。

---

## Core Entities

### 1. Translation Request（翻譯請求）

代表單次翻譯任務，由前端發送至後端 API。

**Attributes**:

| 欄位 | 類型 | 必填 | 說明 | 驗證規則 |
|------|------|------|------|----------|
| `text` | `string` | ✅ | 待翻譯文字 | 1-5000 字元 |
| `source_lang` | `string` | ❌ | 來源語言碼（如 `en`, `zh`） | ISO 639-1 格式，若為 `null` 則自動偵測 |
| `target_lang` | `string` | ❌ | 目標語言碼（如 `zh-TW`, `en`） | ISO 639-1 格式，若為 `null` 則根據 `source_lang` 智能切換 |
| `stream` | `boolean` | ❌ | 是否使用串流輸出 | 預設 `true` |

**Example (JSON)**:
```json
{
  "text": "Hello, world!",
  "source_lang": null,
  "target_lang": null,
  "stream": true
}
```

**Backend Schema (Python Pydantic)**:
```python
from pydantic import BaseModel, Field, field_validator

class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="待翻譯文字")
    source_lang: str | None = Field(None, description="來源語言碼，null 表示自動偵測")
    target_lang: str | None = Field(None, description="目標語言碼，null 表示智能切換")
    stream: bool = Field(True, description="是否使用串流輸出")
    
    @field_validator('text')
    def validate_text_not_empty(cls, v):
        if not v.strip():
            raise ValueError('文字不可為空白')
        return v.strip()
```

**Frontend Model (C#)**:
```csharp
public class TranslationRequest
{
    [Required]
    [StringLength(5000, MinimumLength = 1)]
    public string Text { get; set; } = string.Empty;
    
    public string? SourceLang { get; set; }
    public string? TargetLang { get; set; }
    
    public bool Stream { get; set; } = true;
}
```

---

### 2. Translation Response（翻譯回應）

代表翻譯結果，由後端回傳給前端。

**Attributes**:

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `translation` | `string` | ✅ | 翻譯後文字 |
| `source_lang` | `string` | ✅ | 實際使用的來源語言碼（可能來自自動偵測） |
| `target_lang` | `string` | ✅ | 實際使用的目標語言碼 |
| `detected` | `boolean` | ✅ | 是否為自動偵測語言 |

**Example (JSON)**:
```json
{
  "translation": "你好，世界！",
  "source_lang": "en",
  "target_lang": "zh",
  "detected": true
}
```

**Backend Schema (Python Pydantic)**:
```python
class TranslationResponse(BaseModel):
    translation: str = Field(..., description="翻譯後文字")
    source_lang: str = Field(..., description="實際來源語言碼")
    target_lang: str = Field(..., description="實際目標語言碼")
    detected: bool = Field(False, description="是否為自動偵測")
```

**Frontend Model (C#)**:
```csharp
public class TranslationResponse
{
    public string Translation { get; set; } = string.Empty;
    public string SourceLang { get; set; } = string.Empty;
    public string TargetLang { get; set; } = string.Empty;
    public bool Detected { get; set; }
}
```

**SSE Streaming Format** (逐 token 推送):
```
data: {"token": "你", "done": false}\n\n
data: {"token": "好", "done": false}\n\n
data: {"token": "，", "done": false}\n\n
data: {"token": "世界", "done": false}\n\n
data: {"token": "！", "done": true, "source_lang": "en", "target_lang": "zh", "detected": true}\n\n
```

---

### 3. Language（語言）

代表系統支援的語言選項。

**Attributes**:

| 欄位 | 類型 | 必填 | 說明 | 範例 |
|------|------|------|------|------|
| `code` | `string` | ✅ | ISO 639-1 語言碼 | `en`, `zh`, `zh-TW` |
| `name` | `string` | ✅ | 語言顯示名稱 | `English`, `Chinese` |
| `native_name` | `string` | ❌ | 語言本地名稱 | `English`, `中文` |

**Example (JSON)**:
```json
{
  "code": "zh-TW",
  "name": "Chinese (Traditional)",
  "native_name": "中文（繁體）"
}
```

**Backend Schema (Python Pydantic)**:
```python
class Language(BaseModel):
    code: str = Field(..., description="ISO 639-1 語言碼")
    name: str = Field(..., description="語言英文名稱")
    native_name: str | None = Field(None, description="語言本地名稱")
```

**Frontend Model (C#)**:
```csharp
public class Language
{
    public string Code { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? NativeName { get; set; }
}
```

**Supported Languages** (初期 15+ 種，主要為繁體中文與英文):
```json
[
  {"code": "en", "name": "English", "native_name": "English"},
  {"code": "zh-TW", "name": "Traditional Chinese", "native_name": "繁體中文"},
  {"code": "ja", "name": "Japanese", "native_name": "日本語"},
  {"code": "ko", "name": "Korean", "native_name": "한국어"},
  {"code": "fr", "name": "French", "native_name": "Français"},
  {"code": "de", "name": "German", "native_name": "Deutsch"},
  {"code": "es", "name": "Spanish", "native_name": "Español"},
  {"code": "pt", "name": "Portuguese", "native_name": "Português"},
  {"code": "ru", "name": "Russian", "native_name": "Русский"},
  {"code": "it", "name": "Italian", "native_name": "Italiano"},
  {"code": "ar", "name": "Arabic", "native_name": "العربية"},
  {"code": "hi", "name": "Hindi", "native_name": "हिन्दी"},
  {"code": "th", "name": "Thai", "native_name": "ไทย"},
  {"code": "vi", "name": "Vietnamese", "native_name": "Tiếng Việt"},
  {"code": "id", "name": "Indonesian", "native_name": "Bahasa Indonesia"}
]
```

---

### 4. Translation History（翻譯記錄）

代表使用者的歷史翻譯記錄，**僅存在於瀏覽器記憶體中**，不做持久化。

**Attributes**:

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `id` | `string` | ✅ | 唯一識別碼（前端生成 UUID） |
| `original_text` | `string` | ✅ | 原文 |
| `translated_text` | `string` | ✅ | 譯文 |
| `source_lang` | `string` | ✅ | 來源語言碼 |
| `target_lang` | `string` | ✅ | 目標語言碼 |
| `detected` | `boolean` | ✅ | 是否為自動偵測 |
| `timestamp` | `DateTime` | ✅ | 翻譯時間 |
| `is_error` | `boolean` | ✅ | 是否為錯誤訊息 |
| `error_message` | `string` | ❌ | 錯誤訊息（若 `is_error = true`） |

**Frontend Model (C# - Blazor State)**:
```csharp
public class TranslationHistory
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string OriginalText { get; set; } = string.Empty;
    public string TranslatedText { get; set; } = string.Empty;
    public string SourceLang { get; set; } = string.Empty;
    public string TargetLang { get; set; } = string.Empty;
    public bool Detected { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.Now;
    public bool IsError { get; set; }
    public string? ErrorMessage { get; set; }
}
```

**Storage**: 
- 前端使用 Blazor 元件狀態管理（`List<TranslationHistory>`）
- 頁面重新整理或關閉時自動清除
- 無需後端 API 支援

---

### 5. Health Check Response（健康檢查回應）

用於監控服務狀態與模型載入情況。

**Attributes**:

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `status` | `string` | ✅ | 服務狀態 (`ok`, `degraded`, `error`) |
| `model` | `string` | ✅ | 載入的模型名稱（如 `Translategemma-4b-it`） |
| `device` | `string` | ✅ | 推論裝置（`cuda`, `mps`, `cpu`） |
| `model_loaded` | `boolean` | ✅ | 模型是否已載入完成 |
| `uptime_seconds` | `integer` | ❌ | 服務運行時間（秒） |

**Example (JSON)**:
```json
{
  "status": "ok",
  "model": "Translategemma-4b-it",
  "device": "cuda",
  "model_loaded": true,
  "uptime_seconds": 3600
}
```

**Backend Schema (Python Pydantic)**:
```python
from enum import Enum

class HealthStatus(str, Enum):
    OK = "ok"
    DEGRADED = "degraded"
    ERROR = "error"

class HealthCheckResponse(BaseModel):
    status: HealthStatus
    model: str
    device: str
    model_loaded: bool
    uptime_seconds: int | None = None
```

---

## Entity Relationships

```
┌─────────────────────┐
│  Frontend (Blazor)  │
└──────────┬──────────┘
           │
           │ HTTP POST /api/translate
           ▼
    ┌─────────────────┐
    │ TranslationRequest │
    └──────────┬────────┘
               │
               ▼
    ┌──────────────────┐        ┌───────────────┐
    │   Backend API    │───────►│ TranslateGemma │
    │    (FastAPI)     │        │     Model      │
    └──────────┬───────┘        └───────────────┘
               │
               │ SSE Stream (逐 token)
               ▼
    ┌─────────────────────┐
    │ TranslationResponse  │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ TranslationHistory   │ (前端記憶體)
    └──────────────────────┘
```

**說明**:
1. 前端發送 `TranslationRequest` 至後端
2. 後端載入 TranslateGemma 模型進行推論
3. 後端透過 SSE 串流逐 token 回傳 `TranslationResponse`
4. 前端將結果儲存到 `TranslationHistory` 記憶體列表中

---

## State Transitions

### Translation Request Lifecycle

```
┌─────────────┐
│   Created   │  使用者輸入文字並點擊送出
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Validating  │  前端驗證（字數、非空白）
└──────┬──────┘
       │
       ├─→ [Invalid] ──→ Toast 錯誤提示
       │
       ▼
┌─────────────┐
│   Sending   │  發送 HTTP POST /api/translate
└──────┬──────┘
       │
       ├─→ [Network Error] ──→ 對話區域錯誤泡泡
       │
       ▼
┌─────────────┐
│  Streaming  │  接收 SSE token stream
└──────┬──────┘
       │
       ├─→ [Timeout 120s] ──→ 對話區域錯誤泡泡
       ├─→ [Stream Error] ──→ 對話區域錯誤泡泡
       │
       ▼
┌─────────────┐
│  Completed  │  翻譯完成，儲存到 TranslationHistory
└─────────────┘
```

**State Descriptions**:

| 狀態 | 說明 | 錯誤處理 |
|------|------|---------|
| **Created** | 使用者開始輸入文字 | - |
| **Validating** | 前端驗證輸入（1-5000 字元、非空白） | Toast 提示 |
| **Sending** | 發送請求到後端 | 對話泡泡顯示連線錯誤 |
| **Streaming** | 接收 SSE 串流，逐 token 渲染 | 保留部分譯文 + 錯誤泡泡 |
| **Completed** | 翻譯完成，加入歷史記錄 | - |

---

## Data Validation Rules

### Input Validation (前端 + 後端雙重驗證)

| 欄位 | 規則 | 前端驗證 | 後端驗證 |
|------|------|---------|---------|
| `text` | 1-5000 字元 | ✅ Blazor DataAnnotations | ✅ Pydantic Field |
| `text` | 非空白 | ✅ `.trim()` 檢查 | ✅ `validator` |
| `source_lang` | ISO 639-1 或 `null` | ✅ Regex `/^[a-z]{2}(-[A-Z]{2})?$/` | ✅ 語言碼白名單 |
| `target_lang` | ISO 639-1 或 `null` | ✅ Regex `/^[a-z]{2}(-[A-Z]{2})?$/` | ✅ 語言碼白名單 |

### Business Rules

1. **自動語言偵測**:
   - 若 `source_lang` 為 `null`，後端執行語言偵測
   - 若偵測失敗，回傳錯誤要求使用者手動選擇

2. **智能語言切換**:
   - 若 `target_lang` 為 `null`：
     - `source_lang == "zh-TW"` → `target_lang = "en"`（繁體中文 → 英文）
     - `source_lang == "en"` → `target_lang = "zh-TW"`（英文 → 繁體中文）
     - 其他語言 → 回傳錯誤

3. **相同語言對檢查**:
   - `source_lang == target_lang` → Toast 提示「來源與目標語言相同」

---

## Error Models

### Standard Error Response

**Attributes**:

| 欄位 | 類型 | 說明 |
|------|------|------|
| `error` | `string` | 錯誤類型（如 `validation_error`, `timeout`, `model_not_loaded`） |
| `message` | `string` | 友善的錯誤訊息 |
| `details` | `object` | 可選的詳細錯誤資訊 |

**Example (JSON)**:
```json
{
  "error": "timeout",
  "message": "翻譯逾時，請稍後重試",
  "details": {
    "elapsed_seconds": 120
  }
}
```

**Common Error Types**:

| 錯誤碼 | HTTP Status | 訊息範例 | 顯示方式 |
|--------|------------|---------|---------|
| `validation_error` | 422 | 「文字過長，請限制在 5000 字元以內」 | Toast |
| `empty_input` | 422 | 「請輸入文字」 | Toast |
| `timeout` | 504 | 「翻譯逾時，請稍後重試」 | 對話泡泡 |
| `model_not_loaded` | 503 | 「模型初始化中，請稍候片刻」 | 對話泡泡 |
| `unsupported_language` | 400 | 「不支援的語言對」 | Toast |
| `internal_error` | 500 | 「系統錯誤，請稍後重試」 | 對話泡泡 |

---

## Summary

本資料模型設計遵循以下原則：
1. ✅ **無狀態設計**: 所有資料僅用於請求/回應，無資料庫依賴
2. ✅ **雙重驗證**: 前後端均驗證輸入，確保資料完整性
3. ✅ **類型安全**: 使用 Pydantic (Python) 和 DataAnnotations (C#) 確保類型正確
4. ✅ **擴展彈性**: 語言清單可動態擴展，無需修改模型結構

**Status**: ✅ All entities, attributes, relationships, and validation rules defined  
**Next Step**: Generate API contracts (OpenAPI specification)
