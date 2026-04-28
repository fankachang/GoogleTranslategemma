# 快速上手：語系選擇器與互換功能

**Feature Branch**: `001-lang-selector-swap`  
**Date**: 2026-04-28

---

## 功能說明

本功能新增語系選擇器列（來源語系 ↔ 目的語系），透過 `config.yaml` 開關控制是否顯示。

---

## 1. 啟用功能開關

在 `config.yaml`（專案根目錄）新增：

```yaml
features:
  language_selector: true
```

> **預設值**：`false`（功能關閉）。若 `config.yaml` 中沒有此設定，功能自動關閉，介面不顯示語系選擇器列。

---

## 2. 後端修改

### 2a. `backend/src/config.py`

在 `load_config()` 的 `setdefault` 區塊新增：

```python
config.setdefault("features", {})
config["features"].setdefault("language_selector", False)
```

### 2b. `backend/src/routes/config.py`

擴充 `GET /api/config` 回傳值：

```python
features_cfg = app_config.get("features", {})
language_selector = features_cfg.get("language_selector", False)
if not isinstance(language_selector, bool):
    language_selector = False

return {
    "max_input_length": max_input_length,
    "features": {
        "language_selector": language_selector
    }
}
```

---

## 3. 前端修改

### 3a. `frontend/Models/AppConfigResponse.cs`

將現有 positional record 改為 init-only properties，新增 `FeaturesConfig`：

```csharp
public record AppConfigResponse
{
    [JsonPropertyName("max_input_length")]
    public int MaxInputLength { get; init; } = 512;

    [JsonPropertyName("features")]
    public FeaturesConfig Features { get; init; } = new();
}

public record FeaturesConfig
{
    [JsonPropertyName("language_selector")]
    public bool LanguageSelector { get; init; } = false;
}
```

### 3b. `frontend/AppConfig.cs`

新增屬性：

```csharp
public bool LanguageSelectorEnabled { get; set; } = false;
```

### 3c. `frontend/Pages/Index.razor`

在 `OnInitializedAsync` 中讀取設定：

```csharp
AppCfg.LanguageSelectorEnabled = cfg.Features.LanguageSelector;
```

在固定底部 input 區 `<div>` 內，`<TranslationInput>` 之前插入：

```razor
@if (AppCfg.LanguageSelectorEnabled && languages.Count > 0)
{
    <div style="width:@(AppCfg.ContentWidthPercent)%; margin: 0 auto 8px;">
        <div style="display:flex; align-items:center; gap:8px;">
            <LanguageSelector ShowAuto="true" Languages="languages"
                              Value="@sourceLang" ValueChanged="OnSourceLangChanged" />
            <MudIconButton Icon="@Icons.Material.Filled.SwapHoriz"
                           OnClick="SwapLanguages" Disabled="@isLoading" />
            <LanguageSelector ShowAuto="true" Languages="languages"
                              Value="@targetLang" ValueChanged="OnTargetLangChanged" />
        </div>
    </div>
}
```

---

## 4. 驗證步驟

### 功能開啟時

1. 設定 `config.yaml` 中 `features.language_selector: true`
2. 啟動後端 → `GET /api/config` 回傳 `{ ..., "features": { "language_selector": true } }`
3. 開啟前端 → 翻譯輸入框上方顯示語系選擇器列
4. 點擊 ↔ 按鈕 → 兩側語系值互換
5. 選擇「zh-TW」→ 另一側自動變為「en」（FR-009）
6. 兩側選擇相同語系 → 顯示警告，但仍可翻譯（FR-008）

### 功能關閉時

1. 設定 `features.language_selector: false`（或刪除該設定）
2. 前端不顯示語系選擇器列
3. 翻譯以自動偵測模式運作（現有行為，不受影響）

---

## 5. 測試檔案

| 檔案 | 說明 |
|---|---|
| `backend/tests/unit/test_config_features.py` | 測試 `load_config()` 的 `features` 預設值 |
| `backend/tests/integration/test_api_config.py` | 測試 `GET /api/config` 回傳 `features` 欄位 |

---

## 相關 Spec 文件

- 規格：[spec.md](../spec.md)
- 資料模型：[data-model.md](../data-model.md)
- API 合約：[contracts/api-config.md](../contracts/api-config.md)、[contracts/api-languages.md](../contracts/api-languages.md)
- 研究報告：[research.md](../research.md)
