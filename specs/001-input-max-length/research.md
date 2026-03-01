# Research: 可設定的翻譯輸入字數上限

**Phase**: 0 — Outline & Research  
**Branch**: `001-input-max-length`  
**Date**: 2026-03-01

---

## 1. 前端如何在 runtime 取得後端設定值

**Decision**: 後端新增 `GET /api/config` 輕量端點，前端 Blazor WASM 於 `Program.cs` 初始化時以 `HttpClient` 呼叫取得，並注入至單例 `AppConfig.MaxInputLength`。

**Rationale**:
- Spec 澄清（2026-02-19）明確指定此方案，確保 FR-006「前後端單一設定來源」。
- Blazor WASM 不可直接讀取伺服器端 `config.yaml`，必須透過 API 橋接。
- `Program.cs` 的 `builder.Build()` 前是最早的初始化點，此時尚未渲染任何元件，故在此呼叫不影響使用者體驗。

**Alternatives considered**:
- *靜態 `appsettings.json` 於前端部署時寫入*：部署者需手動同步兩個設定檔，違反 FR-006。
- *環境變數注入前端*：Blazor WASM 環境變數在執行時不可讀取，且需要建置時期注入，不支援熱更新設定。

---

## 2. 後端 Pydantic schema 的 `max_length` 策略

**Decision**: `TranslationRequest.text` 欄位的 `max_length` 改為 `10000`（硬上限），route 層 `translate_endpoint` 在 Pydantic 驗證通過後再比對 `config.max_input_length`（業務上限），超過則回傳 HTTP 422。

**Rationale**:
- Pydantic `max_length` 為靜態、建置時期決定，無法讀取動態的 `app.state.config`。
- 硬上限 10,000 防止惡意超大 payload；業務驗證 512（或管理員設定值）為正常使用邊界。
- 兩層驗證責任明確：schema 層防濫用，route 層執行業務規則。
- 現有測試與文件均以 `5000` 為舊硬上限，改為 `10000` 不破壞正常使用情境。

**Alternatives considered**:
- *完全移除 schema max_length*：不安全，極大 payload 可在 Pydantic 驗證前即佔用記憶體。
- *schema max_length 設為動態*：Pydantic v2 不支援在欄位定義時讀取執行時期設定；需 custom validator，複雜度過高。

---

## 3. 後端超限錯誤回應格式

**Decision**: HTTP 422，body 格式 `{"detail": "輸入文字超過允許上限（{limit} 字元）"}`，`{limit}` 替換為實際設定值。

**Rationale**:
- Spec 澄清（2026-03-01）已明確指定此格式（FR-005）。
- 422 Unprocessable Entity 語意正確（資料格式合法但業務規則不通過）。
- `detail` 欄位與 FastAPI / Pydantic 的既有錯誤格式一致，前端可統一處理。

**Alternatives considered**:
- *HTTP 400*：語意偏向「格式錯誤」，422 更精確。
- *HTTP 413 Payload Too Large*：通常用於 HTTP 傳輸層限制，非業務邏輯驗證。

---

## 4. 字元計數單位

**Decision**: Unicode code points（`str.length` in C# = UTF-16 code units，但 BMP 字元 code unit = code point；後端 Python `len()` = code points）。

**Rationale**:
- Spec FR-009 明確要求「Unicode 字元（程式碼點）為單位，不以位元組為單位」。
- Python `len("中文")` = 2（code points），C# `"中文".Length` = 2（BMP 字元 UTF-16 = code points），兩者對 BMP 字元一致。
- 非 BMP 字元（Emoji、稀有漢字）在 C# 中為 surrogate pair（Length = 2）但在 Python 中為 1 code point，存在差異；但 Spec 明確以「Unicode code points」為準，前端顯示值與後端驗證值可能有最多 1 差異（可接受，實際使用場景罕見）。

**Alternatives considered**:
- *UTF-8 位元組數*：中文 3 bytes/char，會讓使用者體感上限降至約 170 字，與預期嚴重不符。

---

## 5. 前端 `/api/config` 失敗處理

**Decision**: `Program.cs` 以 `try/catch` 包裹 HTTP 呼叫，失敗時靜默記錄至 `Console.Error` 並保留 `AppConfig.MaxInputLength = 512`（預設值），不阻擋應用啟動。

**Rationale**:
- Spec FR-011 與澄清（2026-03-01）明確要求靜默回退，不顯示 UI 錯誤。
- 後端可能尚未就緒（容器啟動順序差異），強制中斷前端啟動會造成空白頁面。
- 預設值 512 與後端預設值相同，前後端行為一致。

**Alternatives considered**:
- *顯示 UI 錯誤*：Spec 明確排除此方案。
- *無限重試*：增加複雜度且可能阻擋頁面渲染，Spec 未要求。

---

## 6. config.yaml 無效值處理

**Decision**: `load_config()` 以 `setdefault` 寫入預設值後，再加入驗證：若 `max_input_length` 不為正整數（≤ 0 或非整數），強制覆寫為 512。

**Rationale**:
- Spec Edge Cases 明確要求「設為 0 或負數時回退 512，服務繼續正常運作」。
- `setdefault` 僅處理缺失情況，需額外驗證非法值。

**Alternatives considered**:
- *Pydantic Settings model 驗證*：引入 `pydantic-settings` 套件增加依賴，本功能不值得此成本。

---

## 解決的 NEEDS CLARIFICATION 清單

| 問題 | 解答 | 來源 |
|------|------|------|
| 前端如何取得設定值 | `GET /api/config`，啟動時呼叫 | Spec 澄清 2026-02-19 |
| 後端錯誤狀態碼 | HTTP 422 | Spec 澄清 2026-03-01 |
| `/api/config` 是否需驗證 | 不需要 | Spec 澄清 2026-03-01 |
| 前端失敗處理 | 靜默回退 512 | Spec 澄清 2026-03-01 |
| schema `max_length` 策略 | 硬上限 10000 + route 層業務驗證 | 技術分析 |
| 字元計數單位 | Unicode code points | FR-009 |
| 無效設定值處理 | 回退 512 | Spec Edge Cases |
