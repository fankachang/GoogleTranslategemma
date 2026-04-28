# API Contract: GET /api/config

**Feature Branch**: `001-lang-selector-swap`  
**Date**: 2026-04-28  
**變更類型**: 擴充現有 endpoint（向下相容）

---

## Endpoint

```
GET /api/config
```

**說明**：回傳前端所需的公開設定值，無需驗證。本功能新增 `features` 欄位。

---

## Request

| 項目 | 值 |
|---|---|
| Method | `GET` |
| Path | `/api/config` |
| Headers | 無特殊需求 |
| Body | 無 |
| Auth | 無 |

---

## Response

### 成功（200 OK）

```json
{
  "max_input_length": 512,
  "features": {
    "language_selector": false
  }
}
```

### Schema

| 欄位 | 型別 | 必填 | 說明 |
|---|---|---|---|
| `max_input_length` | `integer` | ✅ | 輸入字元上限（既有欄位，無異動） |
| `features` | `object` | ✅（新增） | 功能旗標物件 |
| `features.language_selector` | `boolean` | ✅（新增） | `true` = 顯示語系選擇器；`false` = 隱藏 |

### 失敗（前端處理策略）

| 情境 | HTTP 狀態 | 前端行為 |
|---|---|---|
| 後端未回應 / 網路錯誤 | 無回應 | 回退 `language_selector: false`，頁面以自動偵測模式運作 |
| 欄位缺失（舊版後端） | 200 | `features` 欄位缺失時 C# 預設值 `new FeaturesConfig()` 生效，`LanguageSelector = false` |

---

## 後端實作位置

**檔案**：`backend/src/routes/config.py`

**擴充前**：
```python
return {"max_input_length": max_input_length}
```

**擴充後**：
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

## 前端消費方式

**檔案**：`frontend/Pages/Index.razor`（`OnInitializedAsync`）

```csharp
try
{
    var cfg = await Http.GetFromJsonAsync<AppConfigResponse>("/api/config");
    if (cfg is not null)
    {
        AppCfg.MaxInputLength = cfg.MaxInputLength;
        AppCfg.LanguageSelectorEnabled = cfg.Features.LanguageSelector;
    }
}
catch
{
    // 回退：MaxInputLength 保持預設 512，LanguageSelectorEnabled 保持 false
    AppCfg.LanguageSelectorEnabled = false;
}
```

---

## 向下相容性

- `max_input_length` 欄位：無異動，現有前端程式碼繼續正常運作。
- `features` 為新增欄位：若前端為舊版（無 `Features` 屬性），JSON 反序列化忽略未知欄位，不拋例外。
