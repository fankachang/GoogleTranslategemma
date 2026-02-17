# Requirements Quality Checklist: TranslateGemma 網頁翻譯服務

**Feature**: 001-gemma-translate-web  
**Created**: 2026-02-18  
**Purpose**: 驗證需求規格的品質、完整性、明確性與一致性（非實作驗證）  
**Scope**: 此檢核表用於檢查「需求是否寫得清楚」，而非「系統是否正確運作」

---

## 檢核說明

此檢核表採用「需求單元測試」方法論，驗證需求文件本身的品質：
- ✅ **正確用法**: 檢查需求是否完整、明確、可測量
- ❌ **錯誤用法**: 驗證系統功能是否正常運作

---

## Requirement Completeness（需求完整性）

檢查所有必要的需求是否已文件化。

- [ ] CHK001 - UI 輸入元件的完整需求是否已定義？包含輸入框類型（單行/多行）、預設值、placeholder 文字 [Completeness, Spec §FR-001]
- [ ] CHK002 - 字數計數器的顯示位置、更新頻率（即時/延遲）、樣式是否已明確定義？ [Gap]
- [ ] CHK003 - 語言下拉選單的預設選項（「自動偵測」還是特定語言）是否已明確指定？ [Completeness, Spec §FR-002]
- [ ] CHK004 - 自動語言偵測失敗時的 fallback 行為是否已定義？ [Gap]
- [ ] CHK005 - 智能語言切換邏輯是否涵蓋所有可能的輸入情境（空白輸入、混合語言、無法辨識語言）？ [Completeness, Spec §FR-002b]
- [ ] CHK006 - 對話泡泡的視覺規格是否完整定義？包含配色、圓角、間距、最大寬度、字體大小 [Gap]
- [ ] CHK007 - 串流輸出中斷後的重試機制或恢復策略是否已定義？ [Gap]
- [ ] CHK008 - 複製按鈕的視覺狀態（hover、active、disabled）需求是否已定義？ [Gap]
- [ ] CHK009 - 翻譯記錄的排序規則（最新在上/在下）是否已明確指定？ [Completeness, Spec §FR-007]
- [ ] CHK010 - 響應式佈局在不同斷點的具體佈局變化（單欄/雙欄、元件隱藏/折疊）是否已定義？ [Completeness, Spec §FR-009]
- [ ] CHK011 - 健康檢查 API 的輪詢頻率或呼叫時機是否已定義？ [Gap]
- [ ] CHK012 - 模型切換（4B ↔ 12B）時是否需要重啟服務的需求是否已說明？ [Gap]
- [ ] CHK013 - 術語對照表的優先級處理邏輯（與模型翻譯結果衝突時）是否已定義？ [Gap, Spec §FR-018]

---

## Requirement Clarity（需求明確性）

檢查需求是否具體、無歧義、可實作。

- [ ] CHK014 - 「對話區域」的精確位置與邊界是否已明確定義？ [Clarity, Spec §FR-004]
- [ ] CHK015 - 「逐 token 方式逐步出現」的視覺效果（淡入/直接出現、動畫時長）是否已量化？ [Ambiguity, Spec §FR-005]
- [ ] CHK016 - 「一鍵複製」是指單次點擊還是包含雙擊、長按等操作？ [Clarity, Spec §FR-006]
- [ ] CHK017 - 「保留在記憶體中」是否定義資料結構型別（陣列/佇列/其他）與清除時機？ [Ambiguity, Spec §FR-007]
- [ ] CHK018 - 「重新整理頁面或關閉瀏覽器」是否包含分頁不活躍（背景執行）等情境？ [Clarity, Spec §FR-008]
- [ ] CHK019 - 響應式斷點的測試裝置尺寸是否涵蓋所有主流裝置（iPhone SE, iPad, Desktop 等）？ [Clarity, Spec §FR-009]
- [ ] CHK020 - 「來源語言碼、目標語言碼」的具體格式（ISO 639-1 / 639-3 / BCP 47）是否已明確？ [Clarity, Spec §FR-010]
- [ ] CHK021 - SSE 串流的重連策略（自動重連次數、間隔）是否已定義？ [Gap]
- [ ] CHK022 - 「系統支援的所有語言」是指當前配置支援的 2 種還是未來可擴充的語言清單？ [Ambiguity, Spec §FR-012]
- [ ] CHK023 - 健康檢查回應中的「服務狀態」可能值（ok/error 之外）是否已列舉完整？ [Clarity, Spec §FR-013]
- [ ] CHK024 - 設定檔中「資料型別」參數的可選值（fp32/fp16/int8）是否已明確列出？ [Clarity, Spec §FR-014]
- [ ] CHK025 - 逾時錯誤訊息中的 `{elapsed}` 格式（秒/分秒）是否已明確定義？ [Clarity, Spec §FR-016]
- [ ] CHK026 - Toast 通知的「3-5 秒自動消失」是固定值還是根據訊息長度動態調整？ [Ambiguity, Spec §FR-017]

---

## Requirement Consistency（需求一致性）

檢查需求之間是否相互矛盾或邏輯衝突。

- [ ] CHK027 - US1.3 提到「超過 1000 字元」與 FR-001a 的「5000 字元上限」是否一致？ [Conflict, Spec §US1.3 vs FR-001a]
- [ ] CHK028 - FR-002 僅支援 zh-TW/en，但 FR-012 要求回傳「所有語言」，定義是否一致？ [Consistency, Spec §FR-002 vs FR-012]
- [ ] CHK029 - SC-001 的 30/60 秒翻譯時間與 FR-016 的 120 秒逾時是否有合理關係？ [Consistency]
- [ ] CHK030 - Edge Cases 中「翻譯逾時」與 FR-016、FR-017 的錯誤處理機制是否一致？ [Consistency]
- [ ] CHK031 - FR-004 對話泡泡布局（右/左）與 US3.4 的描述是否完全一致？ [Consistency]
- [ ] CHK032 - US4 串流輸出需求與 FR-005、FR-011 的技術實作方式是否對齊？ [Consistency]
- [ ] CHK033 - FR-007（記憶體保留）與 FR-008（清除記錄）的觸發時機是否清楚區分？ [Consistency]
- [ ] CHK034 - SC-002 瀏覽器支援與 FR-009 響應式佈局需求是否涵蓋相同裝置範圍？ [Consistency]

---

## Acceptance Criteria Quality（驗收標準品質）

檢查驗收標準是否可測量、可驗證。

- [ ] CHK035 - US1.1 的「30 秒內顯示翻譯結果」是否定義測量起點（點擊送出 vs 後端接收請求）？ [Measurability, Spec §US1.1]
- [ ] CHK036 - US1.4 的「清楚的錯誤訊息泡泡」是否提供具體範例或驗證標準？ [Measurability, Spec §US1.4]
- [ ] CHK037 - US2.5 的「友善提示或自動複製原文」，「或」關係是否代表兩種行為皆可接受？ [Ambiguity, Spec §US2.5]
- [ ] CHK038 - US3.4 的「保持可讀性」是否有量化標準（最小字體、對比度、行高）？ [Measurability, Spec §US3.4]
- [ ] CHK039 - US4.1 的「逐 token 方式逐步出現」如何驗證？是否需要視覺動畫測試？ [Measurability, Spec §US4.1]
- [ ] CHK040 - US4.3 的「視覺回饋」持續時間（2 秒？直到下次操作？）是否已定義？ [Gap, Spec §US4.3]
- [ ] CHK041 - SC-004 的「95% 正常請求」如何定義「正常」？排除哪些異常情境？ [Clarity, Spec §SC-004]
- [ ] CHK042 - SC-005 的「一鍵部署」包含哪些步驟？是否包含模型下載時間？ [Measurability, Spec §SC-005]
- [ ] CHK043 - SC-006 的「不修改程式碼」是否包含修改環境變數或命令列參數？ [Clarity, Spec §SC-006]
- [ ] CHK044 - SC-009 的「清楚的錯誤訊息」是否有明確的評估準則（語言、格式、內容）？ [Measurability, Spec §SC-009]

---

## Scenario Coverage（情境覆蓋）

檢查是否涵蓋所有使用情境與流程。

- [ ] CHK045 - 是否定義使用者首次開啟網頁時的初始狀態（空白畫面 vs 引導訊息）？ [Gap]
- [ ] CHK046 - 是否涵蓋使用者中途修改語言選擇的情境（已輸入文字但未送出）？ [Coverage, Gap]
- [ ] CHK047 - 是否定義連續快速送出多次翻譯請求的處理邏輯（佇列/取消前一次/並行）？ [Gap]
- [ ] CHK048 - 是否涵蓋使用者在串流輸出過程中關閉頁面的情境？ [Coverage, Gap]
- [ ] CHK049 - 是否定義複製功能在不同瀏覽器（Chrome/Firefox/Safari）的相容性需求？ [Coverage, Gap]
- [ ] CHK050 - 是否涵蓋使用者清空輸入框後的 UI 狀態（送出按鈕 disabled？字數歸零？）？ [Gap]
- [ ] CHK051 - 是否定義翻譯記錄達到極大數量（如 1000 筆）時的效能或限制策略？ [Coverage, Gap]
- [ ] CHK052 - 是否涵蓋使用者在不同分頁間切換時的狀態保留需求？ [Coverage, Spec §Edge-多視窗]
- [ ] CHK053 - 是否定義後端服務重啟時前端的偵測與提示機制？ [Gap]
- [ ] CHK054 - 是否涵蓋模型推論較慢（接近但未超過 120 秒）的使用者體驗需求？ [Coverage, Gap]

---

## Edge Case Coverage（邊界案例覆蓋）

檢查邊界條件是否完整定義。

- [ ] CHK055 - 空白輸入的定義是否包含僅有空格、tab、換行等不可見字元的情境？ [Completeness, Spec §Edge-空白輸入]
- [ ] CHK056 - 特殊字元處理是否涵蓋 RTL 語言字元（阿拉伯文、希伯來文）即使目前不支援？ [Coverage, Spec §Edge-特殊字元]
- [ ] CHK057 - 超長文字的處理是否涵蓋恰好 5000 字元的邊界情境？ [Completeness, Spec §Edge-超長文字]
- [ ] CHK058 - 翻譯逾時後使用者是否能重試？重試時是否保留原文？ [Gap, Spec §Edge-翻譯逾時]
- [ ] CHK059 - 模型未載入的錯誤訊息是否包含預估載入時間或進度提示？ [Gap, Spec §Edge-模型未載入]
- [ ] CHK060 - 不支援的語言對錯誤是否會在前端阻擋（避免無效請求）？ [Gap, Spec §Edge-不支援語言對]
- [ ] CHK061 - 多視窗並行時，是否定義同一使用者跨視窗的並發請求數量限制？ [Gap, Spec §Edge-多視窗並行]
- [ ] CHK062 - 是否定義網路極慢（非中斷）導致串流延遲的處理策略？ [Gap]
- [ ] CHK063 - 是否定義輸入包含 SQL injection、XSS 等惡意字串的過濾需求？ [Gap]
- [ ] CHK064 - 是否定義剪貼簿權限被拒絕時的 fallback 行為（手動選取複製？）？ [Gap]
- [ ] CHK065 - 是否定義後端回傳非預期格式（非 JSON/非 SSE）時的前端處理策略？ [Gap]

---

## Non-Functional Requirements（非功能性需求）

檢查效能、安全、可用性等非功能需求是否完整。

- [ ] CHK066 - 是否定義前端載入時間目標（首次載入、後續導航）？ [Gap, NFR-Performance]
- [ ] CHK067 - 是否定義並發使用者數量上限或效能基準（如 50 人同時使用）？ [Completeness, Spec §Scale/Scope]
- [ ] CHK068 - 是否定義 API 請求的 rate limiting 或防濫用機制？ [Gap, NFR-Security]
- [ ] CHK069 - 是否定義輸入文字的安全掃描或過濾需求？ [Gap, NFR-Security]
- [ ] CHK070 - 是否定義 HTTPS/TLS 加密傳輸的強制需求？ [Gap, NFR-Security]
- [ ] CHK071 - 是否定義 CORS 政策的具體來源白名單或允許規則？ [Gap, NFR-Security]
- [ ] CHK072 - 是否定義鍵盤導航（Tab 鍵切換、Enter 送出）的無障礙需求？ [Gap, NFR-Accessibility]
- [ ] CHK073 - 是否定義螢幕閱讀器相容性需求（ARIA 標籤、語意化 HTML）？ [Gap, NFR-Accessibility]
- [ ] CHK074 - 是否定義色彩對比度需求（符合 WCAG 2.1 AA 標準）？ [Gap, NFR-Accessibility]
- [ ] CHK075 - 是否定義後端日誌記錄範圍（錯誤/資訊/除錯）與保留期限？ [Gap, NFR-Observability]
- [ ] CHK076 - 是否定義效能監控指標（回應時間、錯誤率、資源使用）？ [Gap, NFR-Observability]
- [ ] CHK077 - 是否定義服務降級策略（模型卡頓時切換較小模型？限制並發？）？ [Gap, NFR-Reliability]
- [ ] CHK078 - 是否定義備份與還原策略（雖無持久化，但配置檔備份）？ [Gap, NFR-Reliability]

---

## Dependencies & Assumptions（依賴與假設）

檢查外部依賴與隱含假設是否已文件化。

- [ ] CHK079 - 是否明確列出 TranslateGemma 模型的最低版本需求？ [Gap, Dependency]
- [ ] CHK080 - 是否定義本地模型檔案的預期位置與檔案大小（供驗證完整性）？ [Gap, Dependency]
- [ ] CHK081 - 是否假設使用者瀏覽器已啟用 JavaScript？未啟用時的 fallback 是否已定義？ [Assumption, Gap]
- [ ] CHK082 - 是否假設使用者裝置有足夠記憶體保留翻譯記錄？極端情境（記憶體不足）是否已考慮？ [Assumption, Gap]
- [ ] CHK083 - 是否假設後端與前端部署在相同網域（CORS 免除）還是跨域？ [Assumption, Gap]
- [ ] CHK084 - 是否明確依賴特定版本的 FastAPI、Blazor WASM、MudBlazor？ [Dependency, Gap]
- [ ] CHK085 - 是否假設模型推論在單一 GPU/CPU 上進行（非分散式）？ [Assumption]
- [ ] CHK086 - 是否假設網路連線穩定（非間歇性斷線）？間歇性斷線的處理策略是否已定義？ [Assumption, Gap]
- [ ] CHK087 - 是否依賴系統剪貼簿 API（navigator.clipboard）？不支援時的替代方案是否已定義？ [Dependency, Gap]

---

## Traceability & Documentation（追溯性與文件）

檢查需求是否可追溯、版本化、完整記錄。

- [ ] CHK088 - 是否為每個功能需求分配唯一 ID（FR-001 ~ FR-018）以便追溯？ [Traceability, Spec §Requirements]
- [ ] CHK089 - 是否為每個 User Story 分配優先級（P1 ~ P4）並與實作順序對齊？ [Traceability, Spec §User Stories]
- [ ] CHK090 - 是否為每個 Success Criteria 定義驗證方法（自動化測試 / 手動驗證）？ [Gap]
- [ ] CHK091 - 是否記錄每次需求變更的歷史（Clarifications 章節）並標註日期？ [Traceability, Spec §Clarifications]
- [ ] CHK092 - 是否定義需求與設計文件（data-model.md、contracts/openapi.yaml）的對應關係？ [Traceability, Gap]
- [ ] CHK093 - 是否定義需求與實作任務（tasks.md）的對應關係（雙向追溯）？ [Traceability, Gap]
- [ ] CHK094 - 是否為 Key Entities 定義屬性的必填性、資料型別、驗證規則？ [Gap, Spec §Key Entities]
- [ ] CHK095 - 是否記錄團隊決策的理由（為何選擇 Blazor 而非 React？為何 SSE 而非 WebSocket？）？ [Gap]
- [ ] CHK096 - 是否定義術語表（Glossary）統一專業名詞（如「串流」vs「流式」、「翻譯記錄」vs「歷史翻譯」）？ [Gap]

---

## Summary（摘要）

**總檢核項目**: 96 項  
**涵蓋範圍**:
- Requirement Completeness: 13 項
- Requirement Clarity: 13 項
- Requirement Consistency: 8 項
- Acceptance Criteria Quality: 10 項
- Scenario Coverage: 10 項
- Edge Case Coverage: 11 項
- Non-Functional Requirements: 13 項
- Dependencies & Assumptions: 9 項
- Traceability & Documentation: 9 項

**檢核重點**:
- ✅ 驗證需求是否完整、明確、一致
- ✅ 評估驗收標準是否可測量
- ✅ 確認邊界案例與情境覆蓋
- ✅ 檢查非功能需求完整性
- ✅ 評估追溯性與文件品質

**下一步**:
1. 逐項檢核並勾選完成項目
2. 對於未通過的項目，更新 spec.md 補充缺失需求
3. 確保 ≥80% 項目通過後方可進入實作階段

---

**Status**: ✅ Checklist Generated  
**Date**: 2026-02-18  
**Reviewer**: _[待填寫]_
