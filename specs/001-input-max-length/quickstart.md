# Quickstart: 可設定的翻譯輸入字數上限

**Branch**: `001-input-max-length`

本指南說明如何在本機驗證本功能的完整行為（設定 → 重啟 → 前端反映）。

---

## 前置條件

- Python 3.11 + `pip install -r backend/requirements.txt`
- .NET 8 SDK（`dotnet --version` ≥ 8.0）
- 已複製 `config.example.yaml` → `config.yaml`（若尚未存在）

---

## 1. 快速驗證：預設值 512

```bash
# 確認 config.yaml 的 translation 區段未設定 max_input_length（或設為 512）
# translation:
#   max_input_length: 512

# 啟動後端
cd backend
uvicorn src.main:app --reload --port 8000

# 另一個終端：確認端點回傳預設值
curl http://localhost:8000/api/config
# 預期回應：{"max_input_length": 512}

# 送出超過 512 字元的請求
python - <<'EOF'
import httpx, json
text = "A" * 513
r = httpx.post("http://localhost:8000/api/translate",
               json={"text": text, "target_lang": "zh-TW"})
print(r.status_code, r.json())
EOF
# 預期：422 {"detail": "輸入文字超過允許上限（512 字元）"}

# 送出恰好 512 字元的請求（邊界值應被接受）
python - <<'EOF'
import httpx
text = "A" * 512
r = httpx.post("http://localhost:8000/api/translate",
               json={"text": text, "target_lang": "zh-TW"})
print(r.status_code)  # 預期 200
EOF
```

---

## 2. 修改設定值並驗證生效

```yaml
# config.yaml — 修改 max_input_length 為 256
translation:
  max_input_length: 256
  max_new_tokens: 512
  timeout: 120
```

```bash
# 重啟後端後確認
curl http://localhost:8000/api/config
# 預期回應：{"max_input_length": 256}
```

---

## 3. 啟動前端並觀察 UI 行為

```bash
# 確認後端已在 port 8000 執行，然後：
cd frontend
dotnet run
# 瀏覽器開啟 https://localhost:5001（或 Kestrel 印出的 URL）
```

**驗證步驟**：
1. 開啟頁面 → 輸入框下方應顯示 `0 / 256`（或 `0 / 512` 視設定而定）
2. 輸入文字 → 計數器即時更新
3. 輸入超過上限 → 計數器變紅，「翻譯」按鈕停用
4. 刪回上限以內 → 按鈕恢復可用

---

## 4. 執行後端測試

```bash
cd backend
pytest tests/unit/test_config_route.py -v
pytest tests/integration/test_translate_limit.py -v
```

**預期全部通過**。

---

## 5. 模擬 `/api/config` 失敗（前端回退驗證）

```bash
# 停止後端，直接啟動前端
cd frontend
dotnet run
# 開啟頁面 → 計數器應顯示「0 / 512」（回退預設值）
# 瀏覽器 DevTools Console 應有靜默錯誤記錄，UI 不顯示錯誤
```

---

## 常見問題

| 問題 | 排查方向 |
|------|---------|
| `curl /api/config` 回傳 404 | 確認 `main.py` 已 `include_router(config_router, prefix="/api")` |
| 前端顯示 `0 / 5000`（舊值） | 確認 `TranslationInput.razor` 已套用 `MaxInputLength` 參數，前端已重新建置 |
| 後端回傳 422 但 detail 格式不對 | 確認 `translate_endpoint` 使用 `app_config["translation"]["max_input_length"]` 而非舊 `5000` |
