# Data Model: 語系選擇器與互換功能

**Feature Branch**: `001-lang-selector-swap`  
**Date**: 2026-04-28  
**Phase**: 1 — 設計與合約

---

## 實體定義

### 1. `Language`（語系選項）

**現有實體，無異動**

| 欄位 | 型別 | 說明 |
|---|---|---|
| `code` | `string` | 語系代碼，如 `"zh-TW"`、`"en"` |
| `name` | `string` | 英文名稱，如 `"Chinese (Traditional)"` |
| `native_name` | `string` | 本地語言名稱，如 `"繁體中文"` |

**特殊值**：「自動偵測」不存在於後端 `LANGUAGES` 清單中，由前端在清單頭部插入，代碼為 `null`（前端型別 `string?`）。

---

### 2. `FeaturesConfig`（功能旗標設定）

**新增實體**

#### 後端（config.yaml 結構）

```yaml
features:
  language_selector: false   # bool，預設 false（功能關閉）
```

#### 後端（Python dict，由 load_config() 保證存在）

```python
{
  "features": {
    "language_selector": False  # bool
  }
}
```

#### 前端（C# record）

```csharp
public record FeaturesConfig
{
    [JsonPropertyName("language_selector")]
    public bool LanguageSelector { get; init; } = false;
}
```

**預設值語義**：`false` — 功能關閉，向下相容；`true` — 顯示語系選擇器列。

---

### 3. `AppConfigResponse`（前端消費的 API 回應 DTO）

**擴充現有實體**

#### 擴充前（現有）
```csharp
public record AppConfigResponse(
    [property: JsonPropertyName("max_input_length")] int MaxInputLength
);
```

#### 擴充後（本功能）
```csharp
public record AppConfigResponse
{
    [JsonPropertyName("max_input_length")]
    public int MaxInputLength { get; init; } = 512;

    [JsonPropertyName("features")]
    public FeaturesConfig Features { get; init; } = new();
}
```

**破壞性變更**：無。現有使用 `MaxInputLength` 的程式碼繼續正常運作。

---

### 4. `AppConfig`（前端應用程式設定，Scoped DI）

**擴充現有實體**

#### 新增屬性

```csharp
/// <summary>
/// 是否啟用語系選擇器 UI（從後端 GET /api/config 的 features.language_selector 取得）。
/// </summary>
public bool LanguageSelectorEnabled { get; set; } = false;
```

**設定時機**：應用程式啟動時（`Program.cs` 或 `Index.razor` 的 `OnInitializedAsync`），呼叫 `GET /api/config` 取得後寫入。

---

## 狀態轉換

### 語系選擇器的狀態機（前端 Index.razor）

```
[初始化中]
    │  GET /api/config 成功 + language_selector == true
    │  + GET /api/languages 成功
    ▼
[載入語系中] ─── GET /api/languages 失敗 ──→ [隱藏選擇器列]（自動偵測模式）
    │
    │  語系清單載入完成
    ▼
[就緒] ─── 使用者選擇語系 ──→ [就緒]（觸發 FR-009 檢查）
         │
         ├── 兩側語系相同（非 null）──→ 顯示 inline 警告（仍可送出）
         └── 使用者點擊 ↔ ──→ 交換兩側值（不觸發 FR-009）
```

### FR-009 自動切換邏輯（擬代碼）

```
當使用者變更 selectedSide（"source" 或 "target"）為 newValue：
  otherSide = 另一側當前值

  若 newValue == "zh-TW" 且 (otherSide == null 或 otherSide == "zh-TW")：
    → 另一側設為 "en"

  若 newValue == "en" 且 (otherSide == null 或 otherSide == "en")：
    → 另一側設為 "zh-TW"

  （其他 newValue 或其他 otherSide 值：不觸發自動切換）
  （互換按鈕觸發時：直接交換，不執行上述邏輯）
```

---

## 驗證規則

| 欄位 | 規則 | 錯誤處理 |
|---|---|---|
| `features.language_selector`（yaml） | 必須為 bool；非 bool 時後端 `load_config()` 回退 `False` 並記錄警告 | 服務繼續啟動，不拋例外 |
| `AppConfigResponse.Features`（前端） | JSON 欄位缺失時使用預設值 `new FeaturesConfig()`（`LanguageSelector = false`） | 不拋例外，回退隱藏選擇器 |
| 語系代碼（前端送出） | `source_lang` 和 `target_lang` 均允許 `null`（自動偵測）或 `"zh-TW"` / `"en"` | 後端現有驗證不變 |
