# Research: 語系選擇器與互換功能

**Feature Branch**: `001-lang-selector-swap`  
**Date**: 2026-04-28  
**Phase**: 0 — 研究與未知項目解析

---

## 研究問題清單

從 Technical Context 與規格中提取的待解決未知項目：

1. `GET /api/config` 現有回傳格式是否支援擴充 `features` 區塊？
2. 前端 `AppConfigResponse.cs` 如何消費 `GET /api/config`，能否無破壞性地擴充？
3. `LanguageSelector.razor` 元件是否已支援 `ShowAuto` 參數（「自動偵測」）？
4. `Index.razor` 現有佈局模式，語系列插入位置的限制？
5. 後端 `config.py` 的 `setdefault` 模式是否支援巢狀 dict（`features` 區塊）？
6. Blazor WASM 中 `MudSelect<T>` 是否支援 `T="string?"` nullable 語義，以處理代碼 `null` 的「自動偵測」？
7. 前端現有的 `Program.cs` 服務注入模式，`LanguageService` 是否已注入？

---

## 研究結果

### 1. `GET /api/config` 擴充可行性

**決策**：直接擴充現有 endpoint，不建立新 endpoint。  
**理由**：`backend/src/routes/config.py` 目前僅回傳 `{ "max_input_length": int }`。FastAPI 的 `dict` 回傳模式允許直接新增欄位，無需修改 Pydantic schema。擴充後回傳：`{ "max_input_length": int, "features": { "language_selector": bool } }`。  
**替代方案排除**：新增獨立 `GET /api/features` endpoint 違反 Simplicity（Principle III），且前端需多一次 HTTP 請求。

### 2. 前端 `AppConfigResponse.cs` 擴充策略

**決策**：`AppConfigResponse` 使用 C# `record` 型別，新增 `LanguageSelectorEnabled` 屬性，設預設值 `false`（JSON 欄位缺失時回退）。  
**理由**：現有 `record AppConfigResponse([property: JsonPropertyName("max_input_length")] int MaxInputLength)` 語法使用 positional record。需改為帶預設值的屬性寫法以支援可選欄位。  
**具體做法**：
```csharp
// 改為 init-only properties 以支援可選欄位
public record AppConfigResponse
{
    [JsonPropertyName("max_input_length")] public int MaxInputLength { get; init; } = 512;
    [JsonPropertyName("features")] public FeaturesConfig Features { get; init; } = new();
}

public record FeaturesConfig
{
    [JsonPropertyName("language_selector")] public bool LanguageSelector { get; init; } = false;
}
```
**替代方案排除**：保留 positional record 無法設定個別屬性預設值，欄位缺失時會拋出 `JsonException`。

### 3. `LanguageSelector.razor` 元件現狀確認

**決策**：元件已完整，**不需修改**。  
**確認內容**：
- `[Parameter] public bool ShowAuto { get; set; } = false` — 已有「自動偵測」選項開關
- `[Parameter] public List<Language> Languages { get; set; } = new()` — 動態語系清單
- `[Parameter] public string? Value { get; set; }` — nullable，支援代碼 `null`
- `[Parameter] public EventCallback<string?> ValueChanged { get; set; }` — 支援 nullable 回調  
**結論**：`ShowAuto = true` 即可顯示「自動偵測」，`Value = null` 即為「自動偵測」選中狀態。

### 4. `Index.razor` 佈局插入位置

**決策**：語系選擇器列插入在「輸入框固定底部」的 `<div>` 內，位於 `<TranslationInput>` 之前，與 `ContentWidthPercent` 寬度對齊。  
**理由**：現有佈局為三段式（標題列 / 對話區 / 輸入框底部）。語系選擇器應與輸入框同在底部固定區，視覺上形成「語系列 + 輸入框」的組合，符合 Principle V（UI Layout Consistency）。語系列與輸入框共用同一 `width: ContentWidthPercent%` 的容器。

### 5. 後端 `config.py` 巢狀 dict 支援

**決策**：在 `load_config()` 的 `setdefault` 鏈中，對 `features` 區塊使用巢狀 `setdefault`。  
**具體做法**：
```python
config.setdefault("features", {})
config["features"].setdefault("language_selector", False)
```
**理由**：現有 `setdefault` 模式已支援 `translation`、`glossary` 等頂層 dict，巢狀寫法為自然延伸。`False` 為預設值，確保向下相容。

### 6. Blazor WASM `MudSelect<string?>` nullable 語義

**決策**：使用 `MudSelect T="string?"` 搭配 `null` 代表「自動偵測」。  
**理由**：MudBlazor `MudSelect<T>` 完整支援 nullable reference type。`MudSelectItem T="string?" Value="@((string?)null)"` 可正常選中並觸發 `ValueChanged`。前端比較時使用 `Value == null` 即可識別「自動偵測」狀態，傳後端時對應 `source_lang: null` / `target_lang: null`。  
**注意事項**：現有 `LanguageSelector.razor` 已使用 `T="string"` 而非 `T="string?"`，需在整合時確認型別一致性。若元件參數宣告為 `string?`，Blazor 編譯器可正常處理。

### 7. 前端 `Program.cs` 服務注入現狀

**確認**：`LanguageService` 需確認是否已在 `Program.cs` 中以 `builder.Services.AddScoped<LanguageService>()` 或等效方式注入。若已注入則 `Index.razor` 直接 `@inject LanguageService` 即可；若未注入則需新增。此項在實作時驗證（低風險）。

---

## 決策摘要

| 問題 | 決策 | 決策依據 |
|---|---|---|
| 擴充 `/api/config` 還是新增 endpoint | 擴充現有 endpoint | Simplicity（Principle III），減少 HTTP 請求 |
| AppConfigResponse 擴充語法 | 改為 init-only properties record | 支援可選欄位預設值，JSON 缺失欄位不拋例外 |
| LanguageSelector 元件修改 | 不修改 | 元件已完整支援所有需求參數 |
| 語系列佈局位置 | 輸入框固定底部區內，TranslationInput 上方 | UI 一致性（Principle V），視覺組合邏輯 |
| `features` 巢狀 config | `setdefault` 巢狀寫法 | 與現有模式一致，預設 `False` 向下相容 |
| 自動偵測的 nullable 處理 | `string?` + `null` 代碼 | MudBlazor 原生支援，語義清晰 |

---

## 無需解決的 NEEDS CLARIFICATION 項目

規格中無殘留 NEEDS CLARIFICATION 標記。所有澄清均已在 spec.md Clarifications 區塊記錄完畢。

---

## 潛在風險

| 風險 | 可能性 | 緩解策略 |
|---|---|---|
| `LanguageService` 未在 `Program.cs` 注入 | 低（元件已存在） | 實作前確認 `Program.cs`，若無則 1 行修正 |
| Blazor WASM 中 `string?` / `string` 型別不一致導致編譯警告 | 低 | 統一 `LanguageSelector.razor` 參數型別為 `string?` |
| 後端 `config.yaml` 格式錯誤時 `features` 區塊為非 dict | 極低 | `load_config()` 已有型別驗證，`setdefault` 後加型別檢查 |
