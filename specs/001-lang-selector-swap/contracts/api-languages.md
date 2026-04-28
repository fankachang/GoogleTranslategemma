# API Contract: GET /api/languages

**Feature Branch**: `001-lang-selector-swap`  
**Date**: 2026-04-28  
**變更類型**: 無異動（確認現有合約）

---

## Endpoint

```
GET /api/languages
```

**說明**：回傳目前支援的翻譯語系清單（不含「自動偵測」，由前端插入）。本功能不修改此 endpoint。

---

## Request

| 項目 | 值 |
|---|---|
| Method | `GET` |
| Path | `/api/languages` |
| Headers | 無特殊需求 |
| Body | 無 |
| Auth | 無 |

---

## Response

### 成功（200 OK）

```json
[
  { "code": "zh-TW", "name": "Chinese (Traditional)", "native_name": "繁體中文" },
  { "code": "en",    "name": "English",               "native_name": "English"  }
]
```

### Schema（每個陣列元素）

| 欄位 | 型別 | 必填 | 說明 |
|---|---|---|---|
| `code` | `string` | ✅ | 語系代碼（BCP-47），如 `"zh-TW"` |
| `name` | `string` | ✅ | 英文顯示名稱 |
| `native_name` | `string` | ✅ | 本地語言名稱（用於 UI 顯示） |

---

## 前端消費方式

**服務**：`LanguageService.GetLanguagesAsync()`（現有，不修改）

**前端插入「自動偵測」的邏輯**（在 `Index.razor` 中處理）：

```csharp
var langs = await LanguageService.GetLanguagesAsync();
// langs 為後端回傳的真實語系清單（不含自動偵測）
// UI 中透過 LanguageSelector.razor 的 ShowAuto="true" 參數插入「自動偵測」選項
```

`LanguageSelector.razor` 的 `ShowAuto="true"` 在元件內部負責在清單頭部插入固定的「自動偵測」項目（代碼 `null`）。

---

## 失敗處理

| 情境 | 前端行為 |
|---|---|
| 請求失敗 / 回傳空清單 | 隱藏整個語系選擇器列；頁面以自動偵測模式運作；不顯示錯誤訊息干擾使用者（FR-004） |
| `LanguageService` 內建 catch | 回傳硬編碼的備用清單（zh-TW、en），**但**本功能的 `Index.razor` 整合層需在 `GetLanguagesAsync()` 成功後才顯示選擇器列；`LanguageService` 的備用清單屬保底，不影響本功能的隱藏邏輯 |

> **注意**：`LanguageService.cs` 現有的 catch 區塊回傳硬編碼備用清單，意味著即使後端失敗，`GetLanguagesAsync()` 也不會拋例外。`Index.razor` 應以「回傳清單長度 > 0」作為顯示條件，而非 try/catch。

---

## 後端實作位置

**檔案**：`backend/src/routes/languages.py`（不修改）  
**Schema**：`backend/src/schemas/language.py`（不修改）
